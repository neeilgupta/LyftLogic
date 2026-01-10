from __future__ import annotations

import json
import os
import re
import copy
from services.db import (
    add_plan,
    list_plans,
    get_plan,
    get_latest_plan_version,
    list_plan_versions,
    create_plan_version,
    get_plan_version,
)


from fastapi import APIRouter, HTTPException, Query
from models.plans import (
    GeneratePlanRequest,
    GeneratePlanResponse,
    EditPlanRequest,
    EditPlanResponse,
    PlanEditPatch,
    RestorePlanRequest,
)


from .rules.engine import apply_rules_v1
from openai import OpenAI
from datetime import datetime, timezone
from services.plan_diff import compute_plan_diff



_PENDING_EDIT_MESSAGE: dict[int, str] = {}

router = APIRouter(prefix="/plans", tags=["plans"])
client = None

def get_openai_client():
    global client
    if client is None:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client



# ---------- Prompting ----------

SYSTEM_PROMPT = """You are LyftLogic, a practical gym workout planner.
Return ONLY valid JSON that matches the provided schema. No markdown. No extra keys.

Hard rules (must follow):
- NO cardio before lifting. Do not mention treadmill/bike/stair stepper in warmups.
- Only include cardio AFTER the workout if and only if goal is fat_loss.
- Warmup must be 3–5 simple bullet points. No timers, no sets, no reps, no conditioning drills.
- Do NOT include finishers or cooldowns (schema does not allow them).
- Do NOT use RPE. Use simple effort cues only (e.g., "close to failure on final set").
- Rep recommendations must be ONLY "6-8" or "8-12". Never output "10-15", "12-20", etc.
- Every exercise uses: sets (working sets only, 1–3), reps (recommended), rest_seconds.
- Rest minimums: compounds >= 240 seconds, isolations >= 180 seconds.
- Emphasize consistency: reuse a core exercise pool across weeks and across similar days.
  You may vary sets/order/emphasis by day. Offer 1 alternative per exercise in notes (optional).

Preference handling:
- If user prefers machines: avoid barbell AND Smith machine. Use machines/cables/dumbbells.
- If user prefers barbell compounds: make barbells the primary main lifts when equipment allows.
- Adjust for soreness/constraints: substitute patterns that would aggravate the area.

Time/volume targets by session length:
- <=45 min: 4–5 movements total
- 60 min: 6–8 movements total
- 75–90 min: 7–9 movements total
(Movements = main + accessories)
"""

def build_user_prompt(req: GeneratePlanRequest) -> str:
    return f"""
Generate a {req.days_per_week}-day workout plan.

User details:
- Goal: {req.goal}
- Experience: {req.experience}
- Days/week: {req.days_per_week}
- Session length: {req.session_minutes} minutes
- Equipment: {req.equipment}
- Soreness notes: {req.soreness_notes}
- Constraints: {req.constraints}

Output requirements:
- Keep each session within the session length.
- Warmup: 3–5 simple bullet points, no time/sets/reps.
- Exercises only: main + accessories (no finisher, no cooldown).
- Sets means WORKING sets only (1–3). User does 1 warm-up set before each exercise.
- Reps: recommend only "6-8" or "8-12".
- Rest seconds: compounds >=240, isolations >=180.
- Match movement count bucket for session length.
- Keep exercise selection consistent across the week; reuse the main lifts and vary emphasis/sets/order.
- Include a simple effort cue in notes when helpful (no RPE).
- If helpful, include one alternative in notes like "Alt: ..." (optional).
""".strip()



@router.post("/generate")
def generate_plan(req: GeneratePlanRequest):
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Use JSON schema guidance via response_format with strict JSON
    schema = GeneratePlanResponse.model_json_schema()
    schema["additionalProperties"] = False

    def normalize_openai_json_schema(node):
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                props = node["properties"]
                node["additionalProperties"] = False
                node["required"] = list(props.keys())
            for v in node.values():
                normalize_openai_json_schema(v)
        elif isinstance(node, list):
            for item in node:
                normalize_openai_json_schema(item)

    normalize_openai_json_schema(schema)

    # ensure an OpenAI client is available when we actually need it
    if not os.getenv("OPENAI_API_KEY"):
        # Keep server bootable without an API key — fail only at call-time
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    # ensure an OpenAI client is available when we actually need it
    client_local = get_openai_client()

    try:
        resp = client_local.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(req)},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "GeneratePlanResponse",
                    "schema": schema,
                    "strict": True,
                },
            },
            temperature=0.4,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)

        plan = GeneratePlanResponse(**data)
        plan = apply_rules_v1(plan=plan, req=req)

        # Build Phase 1 input_state (stored with version 1)
        req_dict = req.model_dump()

        input_state = {
            **req_dict,

            # Phase 1 editable state (canonical tokens)
            "constraints_tokens": [],
            "preferences_tokens": [],
            "avoid": [],
            "emphasis": None,
            "set_style": None,
            "rep_style": None,

            # Preserve original user constraints text separately
            "base_constraints_text": req_dict.get("constraints", "") or "",
            "chat_history": [],
        }

        # Effective constraints string that rules engine reads
        input_state["constraints"] = input_state["base_constraints_text"]

        saved = add_plan(
            title=plan.title,
            input_json=json.dumps(input_state),
            output_json=plan.model_dump_json(),
        )

        # Effective constraints string that rules engine reads
        input_state["constraints"] = input_state["base_constraints_text"]


        return {"id": saved["id"], "created_at": saved["created_at"], **plan.model_dump()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {e}")
    
@router.get("", summary="List saved plans")
def list_saved_plans(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return {"items": list_plans(limit=limit, offset=offset), "limit": limit, "offset": offset}


@router.get("/{plan_id}", summary="Get a saved plan by id")
def get_saved_plan(plan_id: int):
    row = get_plan(plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")

    latest = get_latest_plan_version(plan_id)

    # ✅ Prefer latest version for BOTH input + output
    if latest:
        input_obj = latest["input"]
        output_obj = latest["output"]
        version = latest["version"]
    else:
        # fallback for older plans created before versioning existed
        input_obj = json.loads(row["input_json"])
        output_obj = json.loads(row["output_json"])
        version = 1

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "title": row["title"],
        "version": version,
        "input": input_obj,
        "output": output_obj,
    }




@router.post("/{plan_id}/edit", summary="Propose an edit to a saved plan", response_model=EditPlanResponse)
def edit_saved_plan(plan_id: int, body: EditPlanRequest) -> EditPlanResponse:
    row = get_plan(plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")

    msg = (body.message or "").strip().lower()
    _PENDING_EDIT_MESSAGE[plan_id] = (body.message or "").strip()


    patch = PlanEditPatch(
        constraints_add=[],
        constraints_remove=[],
        preferences_add=[],
        preferences_remove=[],
        emphasis=None,
        avoid=[],
        set_style=None,
        rep_style=None,
    )
    change_summary: list[str] = []
    errors: list[str] = []

    constraints_map = {
        "no dumbbells": "no_dumbbells",
        "no barbells": "no_barbells",
        "no machines": "no_machines",
        "no cables": "no_cables",
    }
    preferences_map = {
        "prefer cables": "prefer_cables",
        "prefer machines": "prefer_machines",
    }

    for phrase, tok in constraints_map.items():
        if phrase in msg and tok not in patch.constraints_add:
            patch.constraints_add.append(tok)
            change_summary.append(f"Add constraint: {tok}")

    for phrase, tok in preferences_map.items():
        if phrase in msg and tok not in patch.preferences_add:
            patch.preferences_add.append(tok)
            change_summary.append(f"Add preference: {tok}")

    m_focus = re.search(r"\bfocus\s+(arms|chest|back|legs|shoulders)\b", msg)
    if m_focus:
        patch.emphasis = m_focus.group(1)
        change_summary.append(f"Set emphasis: {patch.emphasis}")

    m_avoid = re.search(r"\bavoid\s+(shoulders|knees|lower back)\b", msg)
    if m_avoid:
        avoid_val = m_avoid.group(1).replace(" ", "_")  # lower back -> lower_back
        if avoid_val not in patch.avoid:
            patch.avoid.append(avoid_val)
            change_summary.append(f"Avoid: {avoid_val}")

    can_apply = bool(
        patch.constraints_add
        or patch.constraints_remove
        or patch.preferences_add
        or patch.preferences_remove
        or patch.emphasis
        or patch.avoid
        or patch.set_style
        or patch.rep_style
    )

    if not can_apply:
        errors.append("No recognized edits in message")

    return EditPlanResponse(
        can_apply=can_apply,
        proposed_patch=patch,
        change_summary=change_summary,
        errors=errors,
    )

@router.get("/{plan_id}/versions", summary="List versions for a plan")
def get_plan_versions(plan_id: int):
    row = get_plan(plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {"plan_id": plan_id, "items": list_plan_versions(plan_id)}
# Phase 1 note:
# - constraints_tokens are enforced immediately in the rules engine
# - avoid / emphasis are stored only in input
# - enforcement of avoid / emphasis happens in Phase 2

@router.post("/{plan_id}/apply", summary="Apply a proposed patch to a saved plan (deterministic)")
def apply_plan_patch(plan_id: int, patch: PlanEditPatch):
    row = get_plan(plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")

    latest = get_latest_plan_version(plan_id)
    if not latest:
        # fallback: plan exists but no versions (shouldn’t happen if add_plan creates v1)
        base_input = json.loads(row["input_json"])
        base_output = json.loads(row["output_json"])
        base_version = 1
    else:
        base_input = latest["input"]
        base_output = latest["output"]
        base_version = latest["version"]

    # NOTE: older versions may have extra keys like "_diff" stored in output_json.
    # Make sure base_output is a dict and strip those keys before Pydantic validation.
    new_input = copy.deepcopy(base_input)
    if isinstance(base_output, str):
        base_output = json.loads(base_output)

    if isinstance(base_output, dict):
        base_output.pop("_diff", None)
        # also strip any other private keys just in case
        for k in list(base_output.keys()):
            if str(k).startswith("_"):
                base_output.pop(k, None)

    # ensure Phase 1 keys exist (for older plans)
    new_input.setdefault("constraints_tokens", [])
    new_input.setdefault("preferences_tokens", [])
    new_input.setdefault("avoid", [])
    new_input.setdefault("base_constraints_text", (base_input.get("base_constraints_text") or "").strip())
    new_input.setdefault("emphasis", None)
    new_input.setdefault("set_style", None)
    new_input.setdefault("rep_style", None)
    new_input.setdefault("chat_history", [])


    def apply_add_remove(field: str, add: list[str], remove: list[str]) -> None:
        cur = set(new_input.get(field, []) or [])
        cur = (cur - set(remove)) | set(add)  # add wins
        new_input[field] = sorted(cur)

    apply_add_remove("constraints_tokens", patch.constraints_add, patch.constraints_remove)
    apply_add_remove("preferences_tokens", patch.preferences_add, patch.preferences_remove)

    if patch.avoid:
        new_input["avoid"] = sorted(set(new_input.get("avoid", []) or []).union(set(patch.avoid)))

    if patch.emphasis is not None:
        new_input["emphasis"] = patch.emphasis
    if patch.set_style is not None:
        new_input["set_style"] = patch.set_style
    if patch.rep_style is not None:
        new_input["rep_style"] = patch.rep_style

    # rebuild effective constraints string for rules engine
    def render_constraints_text() -> str:
        parts = []
        base_text = (new_input.get("base_constraints_text") or "").strip()
        if base_text:
            parts.append(base_text)
        if new_input["constraints_tokens"]:
            parts.append("BANS: " + ", ".join(new_input["constraints_tokens"]))
        if new_input["preferences_tokens"]:
            parts.append("PREFER: " + ", ".join(new_input["preferences_tokens"]))
        if new_input["avoid"]:
            parts.append("AVOID: " + ", ".join(new_input["avoid"]))
        if new_input.get("emphasis"):
            parts.append("EMPHASIS: " + str(new_input["emphasis"]))
        return "\n".join(parts).strip()

    new_input["constraints"] = render_constraints_text()

    # Re-run deterministic rules ONLY
    # Your rules signature is apply_rules_v1(plan=GeneratePlanResponse, req=GeneratePlanRequest)
    # Build a lightweight request-like object that includes explicit 'avoid' tokens
    # GeneratePlanRequest is strict (forbids extra fields) so we use a SimpleNamespace
    from types import SimpleNamespace

    req_fields = {k: new_input.get(k) for k in GeneratePlanRequest.model_fields.keys()}
    req_obj = SimpleNamespace(**req_fields, avoid=new_input.get("avoid", []))
    plan_obj = GeneratePlanResponse(**base_output)
    new_plan_obj = apply_rules_v1(plan=plan_obj, req=req_obj)

    new_output = new_plan_obj.model_dump()
        # Reason hint for explainable diffs (deterministic; derived only from patch)
    reason_hint = None
    if patch.avoid and any(str(x).strip().lower() == "shoulders" for x in patch.avoid):
        reason_hint = "avoid_shoulders"
    elif patch.preferences_add and "prefer_cables" in (patch.preferences_add or []):
        reason_hint = "prefer_cables"

    diff = compute_plan_diff(base_output, new_output, reason=reason_hint)



    new_version = base_version + 1
    msg = _PENDING_EDIT_MESSAGE.pop(plan_id, None)

    new_input["chat_history"] = list(new_input.get("chat_history") or [])
    new_input["chat_history"].append({
        "message": msg,
        "patch": patch.model_dump(),
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    })
    create_plan_version(plan_id, new_version, new_input, new_output, diff=diff)
    return {"plan_id": plan_id, "version": new_version, "output": new_output, "diff": diff}

@router.post("/{plan_id}/restore", summary="Restore a previous version by creating a new version snapshot")
def restore_plan_version(plan_id: int, body: RestorePlanRequest):
    row = get_plan(plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")

    target = get_plan_version(plan_id, body.version)
    if not target:
        raise HTTPException(status_code=404, detail="Target version not found")

    latest = get_latest_plan_version(plan_id)
    base_version = latest["version"] if latest else 1
    new_version = base_version + 1

    # Copy EXACTLY (no edits, no recompute)
    restored_input = target["input"]
    restored_output = target["output"]

    diff = {"restored_from": body.version}

    create_plan_version(plan_id, new_version, restored_input, restored_output, diff=diff)

    return {
        "plan_id": plan_id,
        "version": new_version,
        "output": restored_output,
        "diff": diff,
    }
