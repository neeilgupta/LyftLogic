from __future__ import annotations

import json
import os
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from models.plans import GeneratePlanRequest, GeneratePlanResponse
from services.db import add_plan, list_plans, get_plan
from .rules.engine import apply_rules_v1
from openai import OpenAI

router = APIRouter(prefix="/plans", tags=["plans"])
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------- Prompting ----------

SYSTEM_PROMPT = """You are GymGPT, a strength & conditioning coach.
Return ONLY valid JSON that matches the provided schema. No markdown. No extra keys.
Be realistic, safe, and adjust for soreness/constraints. Use common exercise names.
If soreness suggests avoiding a pattern, substitute accordingly (e.g., sore elbows -> reduce heavy pressing).
If the user prefers machines, do not include barbell OR Smith machine movements. Use plate-loaded machines, cables, dumbbells, or bodyweight instead."""

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

Rules:
- Keep it within {req.session_minutes} minutes per session.
- Include warmup, main lifts, accessories, and brief cooldown.
- Use rep ranges appropriate for goal and experience.
- Prefer compound lifts if equipment allows.
- Provide short progression notes for weeks 1-4.
- Output must validate against the JSON schema exactly.
- Prefer rep ranges of 6-8 or 8-12 for most lifts (user preference; avoid very high-rep main work).
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

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "title": row["title"],
        "input": json.loads(row["input_json"]),
        "output": json.loads(row["output_json"]),
    }
