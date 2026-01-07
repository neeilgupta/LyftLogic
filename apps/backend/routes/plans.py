from __future__ import annotations

import json
import os
from services.db import add_plan, list_plans, get_plan, get_latest_plan_version


from fastapi import APIRouter, HTTPException, Query
from models.plans import (
    GeneratePlanRequest,
    GeneratePlanResponse, 
    EditPlanRequest, 
    EditPlanResponse, 
    PlanEditPatch)

from .rules.engine import apply_rules_v1
from openai import OpenAI

router = APIRouter(prefix="/plans", tags=["plans"])
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

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

    


    try:
        resp = client.chat.completions.create(
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


        saved = add_plan(
            title=plan.title,
            input_json=req.model_dump_json(),
            output_json=plan.model_dump_json(),
        )

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

    # ✅ fallback for older plans created before versioning existed
    output_json = latest["output_json"] if latest else row["output_json"]

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "title": row["title"],
        "input": json.loads(row["input_json"]),
        "output": json.loads(output_json),
    }


@router.post("/{plan_id}/edit", summary="Propose an edit to a saved plan (stub)", response_model=EditPlanResponse)
def edit_saved_plan(plan_id: int, body: EditPlanRequest) -> EditPlanResponse:
    # Phase 1 stub: do not parse message, do not modify plans, do not call rules engine.
    # This endpoint exists only to wire frontend -> backend contract.
    row = get_plan(plan_id)
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")

    return EditPlanResponse(
        can_apply=False,
        proposed_patch=PlanEditPatch(),
        change_summary=[],
        errors=["Not implemented"],
    )

