from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from services.nutrition.allergens import build_allergen_set, meal_is_safe, meal_rejection_reason
from services.nutrition.contracts import Meal


@dataclass(frozen=True)
class GenerationRequest:
    # user constraints
    diet: Optional[str]  # "vegan" | "vegetarian" | None
    allergies: list[str]

    # generation controls
    meals_needed: int
    max_attempts: int  # total LLM calls allowed
    batch_size: int    # meals per LLM call


@dataclass(frozen=True)
class GenerationResult:
    accepted: list[dict]
    rejected: list[dict]
    attempts_used: int


def required_diet_tags_for_user(diet: Optional[str]) -> set[str]:
    """
    Maps user diet preference into required diet tags enforced by meal_is_safe().
    Keep it tiny + deterministic.
    """
    if not diet:
        return set()

    d = diet.strip().lower()

    if d == "vegan":
        return {"vegan"}

    if d == "vegetarian":
        return {"vegetarian"}

    if d == "pescatarian":
        return {"pescatarian"}

    # Fail-open: unknown diet strings impose no required tags
    return set()


# LLM function signature:
# returns a list of meal dicts, each with:
#  { name: str, ingredients: [ {name, contains, diet_tags, is_compound}, ... ] }
LLMGenerator = Callable[[GenerationRequest, int], list[Meal]]


def generate_safe_meals(
    req: GenerationRequest,
    llm_generate: LLMGenerator,
) -> GenerationResult:
    """
    Safe generation loop:
      - call LLM in bounded attempts
      - validate every meal fail-closed
      - accept until meals_needed met or attempts exhausted

    IMPORTANT: This function never "fixes" meals. It only accepts or rejects.
    """
    if req.meals_needed <= 0:
        raise ValueError("meals_needed must be > 0")
    if req.max_attempts <= 0:
        raise ValueError("max_attempts must be > 0")
    if req.batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    allergen_set = build_allergen_set(req.allergies)
    required_diet = required_diet_tags_for_user(req.diet)

    accepted: list[dict] = []
    rejected: list[dict] = []
    # Phase 4-G: avoid duplicate template meals across attempts
    accepted_templates: set[str] = set()

    def _template_sig(m: dict) -> str:
        if not isinstance(m, dict):
            return ""
        # Prefer stable identity fields if present
        sig = (
            m.get("template_key")
            or m.get("source_key")
            or m.get("meal_key")
            or m.get("library_key")
            or m.get("name")
            or ""
        )
        return str(sig).strip().lower()




    for attempt in range(1, req.max_attempts + 1):
        candidates = llm_generate(req, attempt)

        # fail-closed: if LLM returns junk, treat as all rejected
        if not isinstance(candidates, list):
            rejected.append({"error": "llm_returned_non_list", "attempt": attempt, "raw": str(type(candidates))})
            continue
        # Phase 4-G: accept unique templates first, then allow repeats as deterministic fallback
        unique_pool: list[Meal] = []
        repeat_pool: list[Meal] = []

        # Prevent duplicates inside the SAME LLM batch too
        seen_this_attempt: set[str] = set()

        for meal in candidates:
            # Always validate safety first (allergies/diet are hard constraints)
            reason = meal_rejection_reason(meal, allergen_set, required_diet_tags=required_diet)
            if reason is not None:
                m = dict(meal) if isinstance(meal, dict) else {"raw": str(meal)}
                m["rejection_reason"] = reason
                rejected.append(m)
                continue

            sig = _template_sig(meal)
            if not sig and isinstance(meal, dict):
                sig = str(meal.get("name") or "").strip().lower()


            # Prefer not-yet-used templates; treat duplicates as fallback
            if sig and (sig in accepted_templates or sig in seen_this_attempt):
                repeat_pool.append(meal)
            else:
                unique_pool.append(meal)
                if sig:
                    seen_this_attempt.add(sig)

        # Accept unique templates only (no repeats across attempts)
        for meal in unique_pool:
            if len(accepted) >= req.meals_needed:
                break

            sig = _template_sig(meal)
            # hard guard: never accept the same template twice
            if sig and sig in accepted_templates:
                continue

            accepted.append(meal)
            if sig:
                accepted_templates.add(sig)



        if len(accepted) >= req.meals_needed:
            return GenerationResult(
                accepted=accepted,
                rejected=rejected,
                attempts_used=attempt,
            )

    return GenerationResult(
        accepted=accepted,
        rejected=rejected,
        attempts_used=req.max_attempts,
    )
