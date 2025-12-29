from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from models.plans import GeneratePlanRequest, GeneratePlanResponse, DayPlan, ExerciseItem


# -----------------------------
# v1 keyword-based helpers
# -----------------------------

def _is_compound(name: str) -> bool:
    n = name.lower()
    # crude v1 heuristic: machines like leg press / hack squat are still "compound" for pattern-capping
    compound_keywords = [
        "bench", "press", "squat", "hack", "leg press", "deadlift", "rdl", "row",
        "pull-up", "pullup", "chin", "pulldown", "overhead", "shoulder press"
    ]
    return any(k in n for k in compound_keywords)

def _pattern(name: str) -> Optional[str]:
    n = name.lower()

    # Order matters (more specific first)
    if "hack" in n or "leg press" in n or "squat" in n:
        return "SQUAT_LEGPRESS"
    if "rdl" in n or "deadlift" in n or "good morning" in n:
        return "HINGE"
    if "pulldown" in n or "pullup" in n or "pull-up" in n or "chin" in n:
        return "VERTICAL_PULL"
    if "row" in n:
        return "HORIZONTAL_PULL"
    if "overhead" in n or "shoulder press" in n or "military" in n:
        return "VERTICAL_PRESS"
    if "bench" in n or "chest press" in n or "incline" in n or "db press" in n or "dumbbell press" in n:
        return "HORIZONTAL_PRESS"

    return None

def _replacement_for_pattern(pattern: str) -> ExerciseItem:
    # Deterministic v1 replacements (isolation)
    if pattern == "HORIZONTAL_PRESS":
        return ExerciseItem(name="Pec Deck", sets=2, reps="10-15", rpe=8, rest_seconds=180, notes="")
    if pattern == "VERTICAL_PRESS":
        return ExerciseItem(name="Lateral Raise", sets=2, reps="12-20", rpe=8, rest_seconds=180, notes="")
    if pattern == "VERTICAL_PULL":
        return ExerciseItem(name="Straight-Arm Pulldown", sets=2, reps="10-15", rpe=8, rest_seconds=180, notes="")
    if pattern == "HORIZONTAL_PULL":
        return ExerciseItem(name="Face Pull", sets=2, reps="12-20", rpe=8, rest_seconds=180, notes="")
    if pattern == "SQUAT_LEGPRESS":
        return ExerciseItem(name="Leg Extension", sets=2, reps="10-15", rpe=8, rest_seconds=180, notes="")
    if pattern == "HINGE":
        return ExerciseItem(name="Seated Leg Curl", sets=2, reps="10-15", rpe=8, rest_seconds=180, notes="")

    # fallback
    return ExerciseItem(name="Cable Curl", sets=2, reps="10-15", rpe=8, rest_seconds=180, notes="")

def _target_rpe_range(experience: str) -> Tuple[int, int, int]:
    """
    Returns (low, high, default)
    beginner: 7-9 (default 8)
    intermediate: 8-10 (default 9)
    advanced: fixed 10 (default 10)
    """
    if experience == "beginner":
        return (7, 9, 8)
    if experience == "intermediate":
        return (8, 10, 9)
    return (10, 10, 10)

def _normalize_reps_str(reps: str, is_compound: bool) -> str:
    """
    v1: gentle normalization toward your recommended bands.
    Only adjusts if range is outside 6-8 or 8-12 for compounds,
    or outside 8-12 for isolations.
    """
    s = reps.strip().lower()
    # expect "a-b" format
    if "-" not in s:
        return reps

    try:
        lo_s, hi_s = s.split("-", 1)
        lo = int(lo_s.strip())
        hi = int(hi_s.strip())
    except Exception:
        return reps

    if is_compound:
        # If compound range goes above 12, pull it back to 8-12 (still hypertrophy-friendly)
        if hi > 12:
            return "8-12"
        # If compound range is very low (e.g. 1-3) push to 6-8
        if hi < 6:
            return "6-8"
        return reps

    # isolation: keep in 8-12 unless it's crazy high
    if hi > 15:
        return "8-12"
    if hi < 8:
        return "8-12"
    return reps



# -----------------------------
# v1 rules engine
# -----------------------------

def apply_rules_v1(plan: GeneratePlanResponse, req: GeneratePlanRequest) -> GeneratePlanResponse:
    # Rule: clamp >5 days unless (advanced AND explicitly requested 6)
    effective_days = req.days_per_week
    explicitly_requested_6 = (req.days_per_week == 6)  # you can refine later using parsing
    if effective_days > 5 and not (req.experience == "advanced" and explicitly_requested_6):
        effective_days = 5

    # If LLM returned more days than allowed, drop extras deterministically
    if len(plan.weekly_split) > effective_days:
        plan.weekly_split = plan.weekly_split[:effective_days]

    # Intensity targets
    rpe_low, rpe_high, rpe_default = _target_rpe_range(req.experience)

    # Set caps
    if req.experience == "advanced":
        sets_min, sets_max, sets_default = 1, 2, 2
    else:
        sets_min, sets_max, sets_default = 1, 3, 2

    # Apply per-day rules
    for day in plan.weekly_split:
        # 1) Pattern cap for COMPOUNDS in day.main (and optionally accessories too)
        _apply_pattern_cap(day)

        # 2) Normalize sets/RPE/rest on all exercises in main + accessories
        for ex in (day.main + day.accessories):
            # sets clamp/default
            if ex.sets is None:
                ex.sets = sets_default
            ex.sets = max(sets_min, min(sets_max, ex.sets))

            if ex.sets >= sets_default:
                ex.sets = sets_default

            # rpe normalize
            if ex.rpe is None:
                ex.rpe = rpe_default
            ex.rpe = max(rpe_low, min(rpe_high, ex.rpe))

            #rep normalization
            ex.reps = _normalize_reps_str(
                ex.reps,
                is_compound=_is_compound(ex.name)
            )


            # rest normalization (HARD OVERRIDE for compounds)
            if _is_compound(ex.name):
                # compounds always get full recovery in this system
                ex.rest_seconds = 240
            else:
            # isolation/accessories: default ~3 min if missing, otherwise clamp
                if ex.rest_seconds is None:
                    ex.rest_seconds = 180
                else:
                    ex.rest_seconds = max(30, min(300, ex.rest_seconds))

        # 3) Beginner safety swaps (v1 shortlist)
        if req.experience == "beginner":
            _apply_beginner_swaps(day, equipment=req.equipment)

    # Optional: attach notes (no UI change required; your schema already has lists)
    _ensure_notes(plan)

    return plan


def _apply_pattern_cap(day: DayPlan) -> None:
    """
    Max 1 compound per movement pattern per session.
    We only apply to day.main in v1 (simple).
    """
    seen: Dict[str, int] = {}  # pattern -> index of kept compound
    new_main: List[ExerciseItem] = []

    for ex in day.main:
        if not _is_compound(ex.name):
            new_main.append(ex)
            continue

        pat = _pattern(ex.name)
        if pat is None:
            new_main.append(ex)
            continue

        if pat not in seen:
            seen[pat] = len(new_main)
            new_main.append(ex)
        else:
            # Replace extra compound with deterministic isolation substitute
            new_main.append(_replacement_for_pattern(pat))

    day.main = new_main


def _apply_beginner_swaps(day: DayPlan, equipment: str) -> None:
    """
    v1: swap a few high-skill barbell moves to controlled equivalents.
    """
    for ex in day.main + day.accessories:
        n = ex.name.lower()

        if "barbell back squat" in n or (("back squat" in n or "squat" in n) and "smith" not in n and "hack" not in n):
            ex.name = "Leg Press" if equipment != "bodyweight" else "Goblet Squat"
        elif "deadlift" in n:
            ex.name = "Dumbbell RDL" if equipment != "bodyweight" else "Hip Hinge"
        elif "good morning" in n:
            ex.name = "Seated Leg Curl" if equipment != "bodyweight" else "Hamstring Bridge"
        elif ("overhead press" in n or "ohp" in n) and "machine" not in n:
            ex.name = "Machine Shoulder Press" if equipment == "full_gym" else "Dumbbell Shoulder Press"


def _ensure_notes(plan: GeneratePlanResponse) -> None:
    # Keep it short/deterministic
    if not plan.progression_notes:
        plan.progression_notes = [
            "Aim to match or slightly beat last session (reps or load) while keeping form strict.",
            "Stop sets when form breaks; effort should be high, but controlled."
        ]
    if not plan.safety_notes:
        plan.safety_notes = [
            "Rest 3–5 min on big compounds and ~3 min on isolation work.",
            "If something feels like a strain or sharp pain, stop and rest."
        ]
