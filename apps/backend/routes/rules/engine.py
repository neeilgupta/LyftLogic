from __future__ import annotations

from typing import List, Optional, Tuple

from models.plans import GeneratePlanRequest, GeneratePlanResponse, DayPlan, ExerciseItem

from routes.rules.exercise_catalog import (
    EXERCISES,
    is_compound,
    is_isolation,
    get_isolations_for_focus,
    get_compounds_for_focus,
    normalize_name,
)

_CANON = {k.lower(): k for k in EXERCISES.keys()}
# -----------------------------
# LyftLogic v2 priorities (minimal set for templates)
# -----------------------------
CHEST_COMPOUND = ["Incline Bench Press", "Chest Press", "Barbell Bench Press"]  # :contentReference[oaicite:4]{index=4}
LAT_COMPOUND = ["Lat Pulldown", "Pull Ups"]                                     # :contentReference[oaicite:5]{index=5}
ROW_CLOSE = ["T-Bar Row (Close grip)", "Chest Supported Rows (Close grip)", "Seated Cable Row"]  # :contentReference[oaicite:6]{index=6}
ROW_WIDE  = ["T-Bar Row (Wide Grip)", "Chest Supported Rows (Wide Grip)", "Seated Cable Row"]   # :contentReference[oaicite:7]{index=7}

QUAD_COMPOUND = ["Hack Squat", "Leg Press", "Bulgarian Split Squat"]            # :contentReference[oaicite:8]{index=8}
HINGE = ["Romanian Dead Lifts", "Romanian Deadlift"]                           # :contentReference[oaicite:9]{index=9}
HIP_THRUST = ["Hipthrust", "Hip Thrust"]                                        # :contentReference[oaicite:10]{index=10}

CHEST_ISO = ["Pec Deck", "Cable Fly (low, mid, high)"]                          # :contentReference[oaicite:11]{index=11}
LATERAL = ["Machine Lateral Raises", "Cable Lateral Raises", "Lateral Raises (DB)", "Lateral Raises"]  # :contentReference[oaicite:12]{index=12}
REAR_DELT = ["Reverse Pec Deck", "Rear Delt Fly (DB)", "Face Pull (rear-delt bias)"]  # :contentReference[oaicite:13]{index=13}

BICEPS = [
    "Preacher Curl",
    "EZ Bar Curl",
    "Incline Dumbbell Curl",
    "EZ Bar Preacher Curl",
    "Dumbbell Curl",
    "Cable Curl",
]

TRI_SIDES = [
    "Triceps Pushdown",
    "V-Bar Tricep Pushdown",
    "Rope Triceps Pushdown",
    "Single-Arm Cable Extension",
]

TRI_OVERHEAD = [
    "Overhead Triceps Extension",
    "Cable Overhead Triceps Extension",
    "Skullcrushers",
    "JM Press",
]
CALVES = ["Seated Calf Raise", "Standing Calf Raise"]                                 # :contentReference[oaicite:17]{index=17}
LEG_EXT = ["Leg Extension (machine)", "Leg Extension"]                                # :contentReference[oaicite:18]{index=18}
HAM_CURL = ["Seated Leg Curl", "Lying Leg Curl"]                                      # :contentReference[oaicite:19]{index=19}
ABS = ["Machine Crunch", "Cable Crunch", "Hanging Leg Raises"]                        # :contentReference[oaicite:20]{index=20}

SHOULDER_PRESS = ["Machine Shoulder Press", "Dumbell Shoulder Press", "Dumbbell Shoulder Press"]  # :contentReference[oaicite:21]{index=21}




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


def _is_barbell_like(name: str) -> bool:
    n = _lc(name)
    return (
        "barbell" in n
        or "bench press" in n
        or "back squat" in n
        or "deadlift" in n
        or "rdl" in n
        or "bent-over barbell row" in n
        or "bent-over barbell rows" in n
    )

def _is_smith(name: str) -> bool:
    return "smith" in _lc(name)


def _normalize_reps(name: str, reps: str) -> str:
    """
    Hard clamp to ONLY "6-8" or "8-12".
    - Compounds default "6-8"
    - Isolations default "8-12"
    """
    r = _lc(reps)
    if r in ("6-8", "8-12"):
        return reps

    if is_compound(name):
        return "6-8"
    return "8-12"

def _normalize_rest_seconds(name: str, rest_seconds: Optional[int]) -> int:
    # Hard mins: compounds >=240, isolations >=180
    if is_compound(name):
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
    Deterministic + cap-safe:
      - trim accessories first
      - replace unknown exercises (curated universe)
      - dedupe within the day
      - enforce compound cap
      - pad isolation-first (no duplicates), compounds only if under cap
    """
    lo, hi = _movement_bucket(req.session_minutes)

    if len(day.main) >= 2 and len(day.accessories) >= 3:
        # still enforce cap + dedupe and exit
        _dedupe_day(day)
        _enforce_compound_cap(day, req.session_minutes)
        _dedupe_day(day)
        return

    def total() -> int:
        return len(day.main) + len(day.accessories)

    # 0) curated universe + dedupe early (so we don't count junk)
    _replace_unknown_exercises(day)
    _dedupe_day(day)

    # 1) trim extras (accessories first)
    while total() > hi and day.accessories:
        day.accessories.pop()

    # 2) enforce compound cap after trimming
    _enforce_compound_cap(day, req.session_minutes)
    _dedupe_day(day)

    # 3) if already meets minimum, stop
    if total() >= lo:
        return

    # 4) pad isolation-first (focus-matched), no duplicates
    existing = {normalize_name(e.name) for e in (day.main + day.accessories)}

    iso_pool = [n for n in get_isolations_for_focus(day.focus) if normalize_name(n) not in existing]
    comp_pool = [n for n in get_compounds_for_focus(day.focus) if normalize_name(n) not in existing]

    def can_add_compound() -> bool:
        return _count_compounds(day) < _compound_cap(req.session_minutes, day.focus)

    while total() < lo:
        if iso_pool:
            name = iso_pool.pop(0)
        elif comp_pool and can_add_compound():
            name = comp_pool.pop(0)
        else:
            break

        day.accessories.append(
            ExerciseItem(
                name=name,
                sets=2,
                reps=_normalize_reps(name, ""),                 # becomes 6-8 or 8-12
                rest_seconds=_normalize_rest_seconds(name, None),
                notes="",
            )
        )
        existing.add(normalize_name(name))

    # 5) final safety pass
    _dedupe_day(day)
    _enforce_compound_cap(day, req.session_minutes)
    _dedupe_day(day)


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
        if is_compound(ex.name):
            if is_lower:
                ex.name = "Barbell Back Squat" if ("squat" in _lc(ex.name) or "leg press" in _lc(ex.name)) else "Romanian Deadlift"
                ex.notes = (ex.notes + " ").strip() + "Alt: Leg Press"
            else:
                ex.name = "Barbell Bench Press" if "press" in _lc(ex.name) else "Bent-Over Barbell Rows"
                ex.notes = (ex.notes + " ").strip() + "Alt: Machine Variation"
            day.main[i] = ex
            break


def _compound_cap(session_minutes: int, focus: str) -> int:
    f = (focus or "").lower()

    # Lower-body override: max 1–2 compounds regardless of time
    if "lower" in f or "leg" in f:
        return 2

    # Upper-body caps scale with session length buckets
    if session_minutes <= 45:
        return 3  # deterministic: use upper bound of 2–3
    if session_minutes <= 60:
        return 4  # deterministic: use upper bound of 3–4
    return 5      # 75–90: upper bound of 4–5


def _count_compounds(day) -> int:
    items = (getattr(day, "main", []) or []) + (getattr(day, "accessories", []) or [])
    cnt = 0
    for ex in items:
        n = normalize_name(ex.name)
        if not n:
            continue
        canon = _CANON.get(n.lower(), n)
        if is_compound(canon):
            cnt += 1
    return cnt

def _replace_unknown_exercises(day) -> None:
    """
    If the LLM outputs an exercise not in the curated catalog,
    replace it with a valid isolation (focus-matched), avoiding duplicates.
    """
    items = (getattr(day, "main", []) or []) + (getattr(day, "accessories", []) or [])
    used = {normalize_name(ex.name) for ex in items if ex.name}

    focus = getattr(day, "focus", "")
    iso_pool = [n for n in get_isolations_for_focus(focus) if normalize_name(n) not in used]
    if not iso_pool:
        iso_pool = [n for n in EXERCISES.keys() if is_isolation(n) and normalize_name(n) not in used]

    for ex in items:
        n = normalize_name(ex.name)
        if not n:
            continue

        # 1) Case-insensitive canonical match
        canon = _CANON.get(n.lower())
        if canon:
            ex.name = canon
            used.add(normalize_name(canon))
            continue

        # 2) Truly unknown → replace with isolation
        if n not in EXERCISES:
            if iso_pool:
                new_name = iso_pool.pop(0)
                ex.name = new_name
                used.add(normalize_name(new_name))


def _dedupe_day(day) -> None:
    items = (getattr(day, "main", []) or []) + (getattr(day, "accessories", []) or [])
    seen = set()
    out = []
    for ex in items:
        n = normalize_name(ex.name)
        if not n:
            continue
        canon = _CANON.get(n.lower(), n)
        nn = normalize_name(canon)
        if nn and nn not in seen:
            ex.name = canon  # normalize stored name too
            out.append(ex)
            seen.add(nn)

    main_len = len(getattr(day, "main", []) or [])
    day.main = out[:main_len]
    day.accessories = out[main_len:]

def _enforce_compound_cap(day, session_minutes: int) -> None:
    cap = _compound_cap(session_minutes, getattr(day, "focus", ""))

    items = (getattr(day, "main", []) or []) + (getattr(day, "accessories", []) or [])
    used = {normalize_name(ex.name) for ex in items if ex.name}

    iso_pool = [n for n in get_isolations_for_focus(getattr(day, "focus", "")) if normalize_name(n) not in used]
    if not iso_pool:
        iso_pool = [n for n in EXERCISES.keys() if is_isolation(n) and normalize_name(n) not in used]

    compounds_seen = 0
    for ex in items:
        n = normalize_name(ex.name)
        if not n:
            continue
        canon = _CANON.get(n.lower(), n)

        if is_compound(canon):
            compounds_seen += 1
            if compounds_seen > cap and iso_pool:
                new_name = iso_pool.pop(0)
                ex.name = new_name
                used.add(normalize_name(new_name))


def _select_day_templates(days_per_week: int) -> list[str]:
    # Your coaching split logic
    if days_per_week <= 2:
        return ["FB_A", "FB_B"][:days_per_week]

    if days_per_week == 3:
        return ["FB_A", "FB_B", "FB_C"]

    if days_per_week == 4:
        return ["UPPER_A", "LOWER_QUAD", "UPPER_B", "LOWER_HAM"]

    if days_per_week == 5:
        return ["UPPER_A", "LOWER_QUAD", "UPPER_B", "LOWER_HAM", "SHARMS"]

    # 6+ (allowed but not recommended): default to PPLPPL
    return ["PUSH", "PULL", "LEGS", "PUSH", "PULL", "LEGS"][:days_per_week]

def _template_to_focus(template_key: str) -> str:
    # This is the string your existing rules/pools can understand
    t = template_key.upper()

    if t.startswith("FB_"):
        return "Full Body"

    if t == "UPPER_A": return "Upper A"
    if t == "UPPER_B": return "Upper B"

    if t == "LOWER_QUAD":
        return "Lower (quad)"
    if t == "LOWER_HAM":
        return "Lower (hamstring)"

    if t == "SHARMS":
        return "Upper (sharms)"

    if t == "PUSH":
        return "Upper (push)"
    if t == "PULL":
        return "Upper (pull)"
    if t == "LEGS":
        return "Lower"

    return "Upper"

def _canon_name(name: str) -> Optional[str]:
    n = normalize_name(name)
    if not n:
        return None
    # case-insensitive canonical mapping to EXERCISES key
    canon = _CANON.get(n.lower())
    if canon:
        return canon
    # if it's already an exact key
    if n in EXERCISES:
        return n
    return None


def _pick_first_valid(priority: List[str], banned: set[str]) -> Optional[str]:
    for raw in priority:
        cn = _canon_name(raw)
        if not cn:
            continue
        nn = normalize_name(cn)
        if nn in banned:
            continue
        if cn in EXERCISES:
            return cn
    return None


def _template_slots(template_key: str) -> Tuple[List[List[str]], List[List[str]]]:
    t = (template_key or "").upper()

    if t == "UPPER_A":
        main = [CHEST_COMPOUND, LAT_COMPOUND, CHEST_ISO]
        acc  = [ROW_CLOSE, LATERAL, BICEPS]
        return main, acc

    if t == "UPPER_B":
        main = [ROW_WIDE, CHEST_COMPOUND, LAT_COMPOUND]
        acc  = [CHEST_ISO, REAR_DELT, BICEPS]
        return main, acc

    if t == "LOWER_QUAD":
        main = [LEG_EXT, QUAD_COMPOUND]
        acc  = [HAM_CURL, HIP_THRUST, CALVES, ABS]
        return main, acc

    if t == "LOWER_HAM":
        main = [HAM_CURL, HINGE]
        acc  = [LEG_EXT, HIP_THRUST, CALVES, ABS]
        return main, acc

    if t == "SHARMS":
        main = [SHOULDER_PRESS]
        acc  = [LATERAL, BICEPS, BICEPS]
        return main, acc

    # fallback: no template overwrite
    return [], []

def _triceps_slots_for_day(template_key: str, has_sharms: bool) -> list[list[str]]:
    t = template_key.upper()

    if t == "SHARMS":
        return [TRI_SIDES, TRI_OVERHEAD]  # both

    if t == "UPPER_A":
        return [TRI_SIDES]  # sides only
    if t == "UPPER_B":
        return [TRI_OVERHEAD]  # overhead only

    # For FB days, we can rotate based on day suffix
    if t.startswith("FB_"):
        if t.endswith("A"):
            return [TRI_SIDES]
        if t.endswith("B"):
            return [TRI_OVERHEAD]
        return [TRI_SIDES]  # FB_C default
    return []

def _apply_template(day: DayPlan, req: GeneratePlanRequest, template_key: str, has_sharms: bool) -> None:
    main_slots, acc_slots = _template_slots(template_key)
    acc_slots = list(acc_slots)  # in case it's a tuple
    acc_slots += _triceps_slots_for_day(template_key, has_sharms)
    
    if not main_slots and not acc_slots:
        return

    banned: set[str] = set()

    def build_items(slots: List[List[str]]) -> List[ExerciseItem]:
        items: List[ExerciseItem] = []
        for slot in slots:
            pick = _pick_first_valid(slot, banned=banned)
            if not pick:
                continue
            banned.add(normalize_name(pick))
            items.append(
                ExerciseItem(
                    name=pick,
                    sets=2,  # your preferred default
                    reps=_normalize_reps(pick, ""),
                    rest_seconds=_normalize_rest_seconds(pick, None),
                    notes="",
                )
            )
        return items

    new_main = build_items(main_slots)
    new_acc = build_items(acc_slots)

    # Hard rule: no shoulder press on upper days that include chest press work
    if template_key.upper() in ("UPPER_A", "UPPER_B"):
        new_main = [ex for ex in new_main if "shoulder press" not in _lc(ex.name)]
        new_acc = [ex for ex in new_acc if "shoulder press" not in _lc(ex.name)]

    day.main = new_main
    day.accessories = new_acc



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

    # ✅ NEW: decide your split/day templates deterministically
    tpls = _select_day_templates(effective_days)
    has_sharms = "SHARMS" in tpls


    # per-day enforcement
    for i, day in enumerate(plan.weekly_split):
        template_key = tpls[i] if i < len(tpls) else tpls[-1]
        day.focus = _template_to_focus(template_key)
        _apply_template(day, req, template_key, has_sharms)


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

        # Enforce movement counts by time bucket
        _trim_or_pad_movements(day, req)
        _dedupe_day(day)
        _enforce_compound_cap(day, req.session_minutes)
        _dedupe_day(day)

        

    # Notes (short, deterministic, matches your philosophy)
    WARMUP_LINE = "Before each main or accessory lift, do 1 lighter warm-up set at ~50% of your working weight."

    def _clean_lines(lines):
        if not lines:
            return []
        out = []
        for s in lines:
            if not s:
                continue
            s2 = str(s).strip()
            if not s2:
                continue
            # remove simple markdown noise if present
            s2 = s2.replace("**", "").replace("__", "")
            out.append(s2)
        return out

    def _ensure_warmup_line(lines):
        hay = " ".join(lines).lower()
        # don't duplicate if model already says it
        if ("50%" in hay) or ("warm-up set" in hay) or ("warm up set" in hay):
            return lines
        return [WARMUP_LINE] + lines

    plan.progression_notes = _clean_lines(plan.progression_notes)
    if not plan.progression_notes:
        plan.progression_notes = [
            "Working sets: take the final set close to failure (0–2 RIR).",
            "Progress week to week by adding a rep or small weight when form stays clean.",
        ]
    plan.progression_notes = _ensure_warmup_line(plan.progression_notes)

    plan.safety_notes = _clean_lines(plan.safety_notes)
    if not plan.safety_notes:
        plan.safety_notes = [
            "No cardio before lifting. If goal is fat loss, add optional cardio after the workout.",
            "Rest >=4 min on compounds and >=3 min on isolations."
        ]


    return plan
