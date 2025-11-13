"""
LLM utilities for GymGPT.

This module wraps OpenAI so the rest of the codebase doesn't have to know
about API details. If you ever swap models, change it here.
"""

import os
from typing import List, Dict, Any

from openai import OpenAI

# Expect OPENAI_API_KEY in environment
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_MODEL = "gpt-4.1-mini"


def explain_workout(plan: Dict[str, Any]) -> str:
    """
    Take a structured workout plan (from build_workout_plan) and return
    a natural-language explanation for the user.
    """
    focus = plan.get("focus", "full body")
    equipment = plan.get("equipment", "gym")
    exercises = plan.get("exercises", [])

    # Build a compact description of the plan to feed to the model
    summary_lines: List[str] = []
    for ex in exercises:
        summary_lines.append(
            f"- {ex['name']}: {ex['sets']}x{ex['reps']} (weight_delta: {ex.get('weight_delta', 0)})"
        )
    summary_text = "\n".join(summary_lines)

    prompt = f"""
You are an experienced strength coach.

The user has this workout plan:

Focus: {focus}
Equipment: {equipment}
Exercises:
{summary_text}

Explain the workout in simple, friendly language.
Include:
- What the focus is
- What the main lifts do
- How the weight changes (weight_delta) should be interpreted
Keep it to about 2–3 short paragraphs.
"""

    try:
        resp = _client.responses.create(
            model=DEFAULT_MODEL,
            input=prompt,
        )
        # New Responses API shape
        return resp.output[0].content[0].text.strip()
    except Exception as e:
        print("LLM error in explain_workout:", e)
        # Let the caller decide how to handle None
        raise


def coach_reply(user_message: str, logs_summary: str = "") -> str:
    """
    Generic 'chat with a coach' helper. You can call this later from a /coach route.
    """
    prompt = f"""
You are a practical strength coach. Answer briefly, clearly, and with concrete steps.

The user said:
\"\"\"{user_message}\"\"\"

Recent training summary:
\"\"\"{logs_summary}\"\"\"

Respond with clear, actionable advice. Avoid fluff.
"""

    try:
        resp = _client.responses.create(
            model=DEFAULT_MODEL,
            input=prompt,
        )
        return resp.output[0].content[0].text.strip()
    except Exception as e:
        print("LLM error in coach_reply:", e)
        raise
