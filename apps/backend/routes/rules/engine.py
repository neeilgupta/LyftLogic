from __future__ import annotations

from typing import List, Optional, Tuple

from models.plans import GeneratePlanRequest, GeneratePlanResponse, DayPlan, ExerciseItem


# -----------------------------
# helpers
# -----------------------------

CARDIO_WORDS = ("treadmill", "elliptical", "bike", "bicycle", "stair", "stepper", "rowing", "rower", "run", "jog")
WARMUP_BAD_TOKENS = ("minute", "minutes", "sec", "seconds", "set", "sets", "rep", "reps")

def _lc(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _wants_machines(req: GeneratePlanRequest) -> bool:
    c = _lc(req.constraints)
    return "prefer machines" in c or "machines only" in c or "machine" in c

def _wants_barbells(req: GeneratePlanRequest) -> bool:
    c = _lc(req.constraints)
    return ("prefer barbell" in c) or ("barbell" in c and "avoid barbell" not in c)

def _is_compound(name: str) -> bool:
    n = _lc(name)
    compound_keywords = (
        "bench", "press", "squat", "leg press", "hack", "deadlift", "rdl", "row",
        "pull-up", "pullup", "chin", "pulldown", "overhead", "shoulder press"
    )
    return any(k in n for k in compound_keywords)

def _is_barbell_like(name: str) -> bool:
    n = _lc(name)
    return ("barbell" in n) or (n.startswith("bench press")) or (n.startswith("back squat")) or ("deadlift" in n)

def _is_smith(name: str) -> bool:
    return "smith" in _lc(name)

def _is_isolation(name: str) -> bool:
    # conservative: if not compound, treat as isolation
    return not _is_compound(name)

def _normalize_reps(name: str, reps: str) -> str:
    """
    Hard clamp to ONLY "6-8" or "8-12".
    - Compounds default "6-8"
    - Isolations default "8-12"
    """
    r = _lc(reps)
    if r in ("6-8", "8-12"):
        return reps

    if _is_compound(name):
        return "6-8"
    return "8-12"

def _normalize_rest_seconds(name: str, rest_seconds: Optional[int]) -> int:
    # Hard mins: compounds >=240, isolations >=180
    if _is_compound(name):
        return 240
    # isolations
    if rest_seconds is None:
        return 180
    return max(180, min(600, rest_seconds))

def _normalize_sets(sets: Optional[int]) -> int:
    # working sets only: 1-3
    if sets is None:
        return 2
    return max(1, min(3, sets))

def _clean_warmup_items(items: List[str]) -> List[str]:
    cleaned: List[str] = []
    for w in items:
        wl = _lc(w)
        if not wl:
            continue

        # Remove anything that looks timed/structured or cardio-ish
        if any(tok in wl for tok in WARMUP_BAD_TOKENS):
            continue
        if any(cw in wl for cw in CARDIO_WORDS):
            continue
        # Remove anything containing digits (e.g., "2 sets", "5 min")
        if any(ch.isdigit() for ch in wl):
            continue

        cleaned.append(w.strip())

    # Cap to 3–5 bullets
    return cleaned[:5]

def _default_warmup_for_focus(focus: str) -> List[str]:
    f = _lc(focus)
    if "lower" in f:
        return [
            "Light hip and hamstring stretch",
            "Quad and calf stretch",
            "Bodyweight squat pattern warm-up",
        ]
    # upper/default
    return [
        "Light shoulder and chest stretch",
        "Band pull-aparts or scap squeezes",
        "Easy arm circles",
    ]

def _movement_bucket(session_minutes: int) -> Tuple[int, int]:
    if session_minutes <= 45:
        return (4, 5)
    if session_minutes <= 60:
        return (6, 8)
    return (7, 9)

def _trim_or_pad_movements(day: DayPlan, req: GeneratePlanRequest) -> None:
    """
    Ensure movements (main + accessories) hit the bucket.
    If too many: trim accessories first.
    If too few: add from deterministic pools (respect prefs).
    """
    lo, hi = _movement_bucket(req.session_minutes)

    def total() -> int:
        return len(day.main) + len(day.accessories)

    # trim extras
    while total() > hi and day.accessories:
        day.accessories.pop()

    # pad if too few
    if total() >= lo:
        return

    pool = _exercise_pool_for_day(day, req)
    existing_names = {_lc(e.name) for e in (day.main + day.accessories)}
    for ex in pool:
        if total() >= lo:
            break
        if _lc(ex.name) in existing_names:
            continue
        day.accessories.append(ex)
        existing_names.add(_lc(ex.name))

def _exercise_pool_for_day(day: DayPlan, req: GeneratePlanRequest) -> List[ExerciseItem]:
    """
    Deterministic "safe defaults" used only to pad movement count.
    Keeps consistency + respects machine/barbell preference.
    """
    machines_only = _wants_machines(req)
    wants_barbell = _wants_barbells(req) and req.equipment == "full_gym" and not machines_only

    f = _lc(day.focus)
    is_lower = "lower" in f

    # Note: sets are working sets (1–3); reps normalized later anyway
    if is_lower:
        base = [
            ExerciseItem(name="Back Squat" if wants_barbell else "Leg Press", sets=2, reps="6-8", rest_seconds=240, notes="Alt: Hack Squat"),
            ExerciseItem(name="Romanian Deadlift" if wants_barbell else "Dumbbell RDL", sets=2, reps="6-8", rest_seconds=240, notes="Alt: Hip Hinge Variation"),
            ExerciseItem(name="Seated Leg Curl", sets=2, reps="8-12", rest_seconds=180, notes="Alt: Lying Leg Curl"),
            ExerciseItem(name="Leg Extension", sets=2, reps="8-12", rest_seconds=180, notes="Alt: Split Squat"),
            ExerciseItem(name="Calf Raise", sets=2, reps="8-12", rest_seconds=180, notes="Alt: Seated Calf Raise"),
        ]
    else:
        base = [
            ExerciseItem(name="Bench Press" if wants_barbell else "Machine Chest Press", sets=2, reps="6-8", rest_seconds=240, notes="Alt: Dumbbell Bench Press"),
            ExerciseItem(name="Incline Bench Press" if wants_barbell else "Incline Dumbbell Press", sets=2, reps="6-8", rest_seconds=240, notes="Alt: Incline Machine Press"),
            ExerciseItem(name="Lat Pulldown", sets=2, reps="6-8", rest_seconds=240, notes="Alt: Pull-Ups"),
            ExerciseItem(name="Seated Cable Row", sets=2, reps="6-8", rest_seconds=240, notes="Alt: Chest-Supported Row"),
            ExerciseItem(name="Lateral Raise", sets=2, reps="8-12", rest_seconds=180, notes="Alt: Cable Lateral Raise"),
            ExerciseItem(name="Triceps Pushdown", sets=2, reps="8-12", rest_seconds=180, notes="Alt: Overhead Triceps Extension"),
            ExerciseItem(name="Biceps Curl", sets=2, reps="8-12", rest_seconds=180, notes="Alt: Cable Curl"),
        ]

    # Machines-only constraint: strip barbells/smith
    if machines_only:
        filtered: List[ExerciseItem] = []
        for ex in base:
            if _is_barbell_like(ex.name) or _is_smith(ex.name):
                continue
            filtered.append(ex)
        return filtered

    return base

def _enforce_barbell_priority(day: DayPlan, req: GeneratePlanRequest) -> None:
    """
    If user prefers barbells and equipment allows, ensure main lifts are barbell-like.
    We do minimal swaps (only if clearly missing).
    """
    if not (_wants_barbells(req) and req.equipment == "full_gym" and not _wants_machines(req)):
        return

    # If main has zero barbell-like compounds, replace first compound-ish main with barbell variant.
    has_barbell = any(_is_barbell_like(e.name) for e in day.main)
    if has_barbell:
        return

    f = _lc(day.focus)
    is_lower = "lower" in f

    for i, ex in enumerate(day.main):
        if _is_compound(ex.name):
            if is_lower:
                ex.name = "Back Squat" if "squat" in _lc(ex.name) or "leg press" in _lc(ex.name) else "Romanian Deadlift"
                ex.notes = (ex.notes + " ").strip() + "Alt: Leg Press"
            else:
                ex.name = "Bench Press" if "press" in _lc(ex.name) else "Barbell Row"
                ex.notes = (ex.notes + " ").strip() + "Alt: Machine Variation"
            day.main[i] = ex
            break


# -----------------------------
# rules engine
# -----------------------------

def apply_rules_v1(plan: GeneratePlanResponse, req: GeneratePlanRequest) -> GeneratePlanResponse:
    # clamp days (keep your existing behavior)
    effective_days = req.days_per_week
    explicitly_requested_6 = (req.days_per_week == 6)
    if effective_days > 5 and not (req.experience == "advanced" and explicitly_requested_6):
        effective_days = 5
    if len(plan.weekly_split) > effective_days:
        plan.weekly_split = plan.weekly_split[:effective_days]

    # per-day enforcement
    for day in plan.weekly_split:
        # Warmup: clean + fallback defaults
        day.warmup = _clean_warmup_items(day.warmup)
        if len(day.warmup) < 3:
            day.warmup = _default_warmup_for_focus(day.focus)

        # Enforce barbell preference in main (minimal)
        _enforce_barbell_priority(day, req)

        # Normalize all exercises
        for ex in (day.main + day.accessories):
            ex.sets = _normalize_sets(ex.sets)
            ex.reps = _normalize_reps(ex.name, ex.reps)
            ex.rest_seconds = _normalize_rest_seconds(ex.name, ex.rest_seconds)

            # notes: remove any RPE-like content if it snuck in
            nl = _lc(ex.notes)
            if "rpe" in nl:
                ex.notes = ""

            # Add a simple effort cue if notes are empty (optional, non-fluffy)
            if not ex.notes.strip():
                ex.notes = "Effort: close to failure on final set."

        # Enforce movement counts by time bucket
        _trim_or_pad_movements(day, req)

    # Notes (short, deterministic, matches your philosophy)
    if not plan.progression_notes:
        plan.progression_notes = [
            "Stick with the same core lifts week to week and try to add a little weight or an extra rep when form stays clean.",
            "Each exercise: do 1 warm-up set, then the listed 1–3 working sets."
        ]
    if not plan.safety_notes:
        plan.safety_notes = [
            "No cardio before lifting. If goal is fat loss, add optional cardio after the workout.",
            "Rest >=4 min on compounds and >=3 min on isolations."
        ]

    return plan
