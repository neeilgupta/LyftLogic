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

import re


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
    "Hammer Curl",

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
HIP_THRUST = ["Smith Machine Hip Thrust", "Machine Hip Thrust"]

ADDUCTOR = ["Machine Hip Adduction", "Hip Adduction"]
ABDUCTOR = ["Machine Hip Abduction", "Hip Abduction"]
CABLE_CRUNCH = ["Cable Crunch"]
FLAT_PRESS = ["Machine Chest Press", "Smith Machine Bench Press", "Chest Press"]
UPPER_BACK_ROW = ["Chest Supported Row", "Machine Row", "Hammer Strength Row", "Seated Cable Row", "T-Bar Row"]


_DB_PAT = re.compile(r"\bdumbbell(s)?\b|\bdb\b", re.I)

# Minimal swap map: feel free to expand over time
_SWAP = {
    # curls
    "incline dumbbell curl": ["Preacher Curl", "Cable Curl", "Machine Curl"],
    "dumbbell curl": ["Cable Curl", "Preacher Curl", "Machine Curl"],
    "hammer curl": ["Rope Hammer Curl", "Cable Curl", "Machine Curl"],

    # presses
    "dumbbell bench press": ["Machine Chest Press", "Smith Machine Bench Press", "Chest Press"],
    "incline dumbbell press": ["Smith Machine Incline Press", "Incline Machine Press", "Incline Dumbbell Press"],
    "incline bench press": ["Incline Machine Press", "Incline Dumbbell Press"],

    # rows
    "dumbbell row": ["Seated Cable Row", "Machine Row", "Chest Supported Row"],

    # squats/hinges (barbell)
    "back squat": ["Hack Squat", "Leg Press", "Smith Machine Squat"],
    "barbell squat": ["Hack Squat", "Leg Press", "Smith Machine Squat"],
    "barbell bench press": ["Smith Machine Bench Press", "Machine Chest Press", "Chest Press"],
    "deadlift": ["Back Extension", "Seated Leg Curl", "Hamstring Curl"],
    "hip thrust": ["Smith Machine Hip Thrust", "Machine Hip Thrust", "Dumbbell Hip Thrust"],
    "romanian deadlift": ["Back Extension", "Seated Leg Curl", "Hamstring Curl"]}



# -----------------------------
# helpers
# -----------------------------

CARDIO_WORDS = ("treadmill", "elliptical", "bike", "bicycle", "stair", "stepper", "rowing", "rower", "run", "jog")
WARMUP_BAD_TOKENS = ("minute", "minutes", "sec", "seconds", "set", "sets", "rep", "reps")

def _lc(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _canon_like(name: str) -> Optional[str]:
    n = normalize_name(name)          # your normalize_name
    if not n:
        return None
    # try exact canonical
    canon = _CANON.get(n.lower())
    if canon:
        return canon
    # fallback: substring contains match (handles punctuation / parenthesis diffs)
    for k in EXERCISES.keys():
        if normalize_name(k) == n:
            return k
    return None


def _wants_machines(req: GeneratePlanRequest) -> bool:
    c = _lc(req.constraints)
    return "prefer machines" in c or "machines only" in c or "machine" in c

def _wants_barbells(req: GeneratePlanRequest) -> bool:
    flags = _notes_flags(req)
    if flags["no_barbells"]:
        return False
    c = _lc(req.constraints)
    return "prefer barbell" in c or "barbells preferred" in c

def _is_barbell_like(name: str) -> bool:
    n = _lc(name)
    return any(k in n for k in (
        "barbell",
        "ez bar",
        "back squat",
        "front squat",
        "deadlift",
        "romanian deadlift",
        "rdl",
        "bent-over barbell row",
        "barbell bench press",
        "t-bar row",
        "barbell overhead press",
        "barbell row",
        "incline bench press",
        "hip thrust"
    ))

# Phase 2: prefer_cables deterministic swaps (only when token is set)
_PREFER_CABLES_SWAP = {
    "pec deck": "Cable Fly",
    "reverse pec deck": "Face Pull",
    "machine lateral raises": "Cable Lateral Raises",
    "machine crunch": "Cable Crunch",
    "preacher curl": "Cable Curl",
    "dumbbell curl": "Cable Curl",
    "incline dumbbell curl": "Cable Curl",
    "overhead triceps extension": "Cable Overhead Triceps Extension",
}

_SHOULDER_BLOCKLIST_SUBSTR = (
    "shoulder press",
    "overhead press",
    "military press",
    "arnold press",
    "lateral raise",
    "lateral raises",
    "upright row",
    "rear delt",
    "reverse pec deck",
    "face pull",
)

# safe, non-shoulder fillers (very conservative)
_AVOID_SHOULDERS_SAFE_ISO = [
    "Cable Curl",
    "Preacher Curl",
    "Triceps Pushdown",
    "Rope Triceps Pushdown",
    "Cable Overhead Triceps Extension",  # keep if you allow overhead triceps even when avoiding shoulders
    "Machine Crunch",
    "Cable Crunch",
    "Seated Leg Curl",
    "Leg Extension (machine)",
    "Seated Calf Raise",
]

def _is_shoulder_dominant(name: str) -> bool:
    n = _lc(name)
    return any(tok in n for tok in _SHOULDER_BLOCKLIST_SUBSTR)

def _first_safe_filler(banned: set[str], req: GeneratePlanRequest) -> Optional[str]:
    """
    Pick a deterministic safe filler that doesn't violate equipment bans.
    """
    flags = _notes_flags(req)
    no_db = flags["no_dumbbells"]
    no_bb = flags["no_barbells"]

    def violates(name: str) -> bool:
        n = (name or "").lower()
        if no_db and (_DB_PAT.search(n) or "dumbbell" in n):
            return True
        if no_bb and _is_barbell_like(n):
            return True
        return False

    for cand in _AVOID_SHOULDERS_SAFE_ISO:
        cn = _canon_name(cand) or cand
        if normalize_name(cn) in banned:
            continue
        if violates(cn):
            continue
        # ensure catalog knows it (optional, but safer)
        if _canon_name(cn) is None and cn not in EXERCISES:
            continue
        return _canon_name(cn) or cn

    return None

def _enforce_avoid_shoulders(day: DayPlan, req: GeneratePlanRequest) -> None:
    flags = _notes_flags(req)
    # REMOVE AFTER TEST: debug print to confirm flags and req.avoid
    # print(f"REMOVE AFTER TEST: avoid_shoulders={flags.get('avoid_shoulders')} req.avoid={getattr(req, 'avoid', None)}")
    if not flags.get("avoid_shoulders", False):
        return

    # If the day is explicitly SHARMS/Shoulder day, we still must produce a valid day
    # but shoulder movements themselves should be removed.
    banned = {normalize_name(e.name) for e in (day.main + day.accessories) if e.name}

    def replace_or_drop(ex: ExerciseItem) -> Optional[ExerciseItem]:
        if not _is_shoulder_dominant(ex.name or ""):
            return ex
        repl = _first_safe_filler(banned, req)
        if not repl:
            return None
        ex.name = repl
        ex.notes = ""
        banned.add(normalize_name(repl))
        return ex

    new_main: list[ExerciseItem] = []
    for ex in (day.main or []):
        r = replace_or_drop(ex)
        if r:
            new_main.append(r)

    new_acc: list[ExerciseItem] = []
    for ex in (day.accessories or []):
        r = replace_or_drop(ex)
        if r:
            new_acc.append(r)

    day.main = new_main
    day.accessories = new_acc


def _enforce_prefer_cables(day, req) -> None:
    flags = _notes_flags(req)
    avoid_shoulders = flags.get("avoid_shoulders", False)
    if not flags.get("prefer_cables", False):
        return

    # machines preference overrides cables preference
    if flags.get("prefer_machines", False):
        return

    no_db = flags.get("no_dumbbells", False)
    no_bb = flags.get("no_barbells", False)

    def violates(name: str) -> bool:
        n = (name or "").lower()
        if no_db and (_DB_PAT.search(n) or "dumbbell" in n):
            return True
        if no_bb and _is_barbell_like(n):
            return True
        return False

    for ex in (day.main + day.accessories):
        key = (ex.name or "").strip().lower()
        target = _PREFER_CABLES_SWAP.get(key)
        if not target:
            continue

        cn = _canon_like(target)
        if not cn:
            continue
        if avoid_shoulders and _is_shoulder_dominant(cn):  
            continue

        # don't swap into something banned
        if violates(cn):
            continue

        ex.name = cn




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

    existing = {normalize_name(e.name) for e in (day.main + day.accessories)}

    # ✅ SHARMS: only allow arm/shoulder isolations as fillers (no random lats/back)
    if "sharms" in _lc(day.focus):
        existing = {normalize_name(e.name) for e in (day.main + day.accessories)}

        # ✅ allow only ONE lateral raise slot total on SHARMS day
        has_lateral = any("lateral raise" in (e.name or "").lower() for e in (day.main + day.accessories))

        sharms_iso = []

        # 1) Prefer another biceps first (best filler)
        for n in BICEPS:
            if normalize_name(n) not in existing:
                sharms_iso.append(n)

        # 2) Then triceps variants (if missing)
        for pool in (TRI_SIDES, TRI_OVERHEAD):
            for n in pool:
                if normalize_name(n) not in existing:
                    sharms_iso.append(n)

        # 3) Only add a lateral raise if we don't already have one
        flags = _notes_flags(req)
        if (not has_lateral) and (not flags.get("avoid_shoulders", False)):
            for n in LATERAL:
                if normalize_name(n) not in existing:
                    sharms_iso.append(n)

        iso_pool = sharms_iso
        comp_pool = []

    else:
        flags = _notes_flags(req)
        iso_pool = [n for n in get_isolations_for_focus(day.focus) if normalize_name(n) not in existing]
        comp_pool = [n for n in get_compounds_for_focus(day.focus) if normalize_name(n) not in existing]

        # If avoiding shoulders, filter out shoulder-dominant movements from filler pools
        if flags.get("avoid_shoulders", False):
            iso_pool = [n for n in iso_pool if not _is_shoulder_dominant(n)]
            comp_pool = [n for n in comp_pool if not _is_shoulder_dominant(n)]

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
    flags = _notes_flags(req)
    if flags["no_barbells"]:
        return
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
                ex.notes = ""
            else:
                ex.name = "Barbell Bench Press" if "press" in _lc(ex.name) else "Bent-Over Barbell Rows"
                ex.notes = ""
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
        return ["FB_A", "REST", "REST", "FB_B", "REST", "REST", "REST"]

    if days_per_week == 3:
        return ["FB_A","REST", "FB_B","REST", "FB_C", "REST","REST"]

    if days_per_week == 4:
        return ["UPPER_A", "LOWER_QUAD", "REST", "UPPER_B", "LOWER_HAM", "REST", "REST"]

    if days_per_week == 5:
        return ["UPPER_A", "LOWER_QUAD", "REST", "UPPER_B", "LOWER_HAM", "SHARMS", "REST"]

    # 6+ (allowed but not recommended): default to PPLPPL
    if days_per_week == 6:
        return ["PUSH", "PULL", "LOWER_QUAD", "CHEST_BACK", "SHARMS", "LOWER_HAM", "REST"]

# 6+ fallback (if ever used)
    return ["PUSH", "PULL", "LOWER_QUAD", "CHEST_BACK", "SHARMS", "LOWER_HAM", "REST"][:days_per_week]

def _template_to_focus(template_key: str) -> str:
    # This is the string your existing rules/pools can understand
    t = template_key.upper()

    if t.startswith("FB_"):
        return "Full Body"

    if t == "UPPER_A": return "Upper A"
    if t == "UPPER_B": return "Upper B"

    if t == "LOWER_QUAD":
        return "Quad Focused Leg Day"
    if t == "LOWER_HAM":
        return "Hamstring Focused Leg Day"

    if t == "SHARMS":
        return "Shoulder and Arms"

    if t == "PUSH":
        return "Push Day(Chest, Shoulders, Triceps)"
    if t == "PULL":
        return "Pull Day(Back, Biceps)"
    if t == "LEGS":
        return "Lower"

    if t == "CHEST_BACK":
        return "Chest/Back"
    if t == "REST":
        return "Rest Day"

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


def _pick_first_valid(priority: List[str], banned: set[str], prefer_machines: bool = False, prefer_cables: bool = False) -> Optional[str]:
    ordered = priority
    if prefer_machines or prefer_cables:
        def score(n: str) -> int:
            nl = n.lower()

            # prefer_machines wins over prefer_cables if both present
            if prefer_machines:
                if "machine" in nl: return 0
                if "smith" in nl: return 1
                if "cable" in nl: return 2
                if "dumbbell" in nl: return 3
                return 4

            # prefer_cables mode
            if "cable" in nl: return 0
            if "machine" in nl: return 1
            if "smith" in nl: return 2
            if "dumbbell" in nl: return 3
            return 4

        ordered = sorted(priority, key=score)


    for raw in ordered:
        cn = _canon_name(raw)
        if not cn:
            continue
        nn = normalize_name(cn)
        if nn in banned:
            continue
        if cn in EXERCISES:
            return cn

    return None


def _row_pool(req: GeneratePlanRequest):
    if _wants_machines(req):
        return [
            "Machine Row",
            "Hammer Strength Row",
            "Seated Cable Row",
            "Chest Supported Row",
        ]
    if "no barbells" in _lc(req.constraints):
        return [
            "Chest Supported Row",
            "Machine Row",
            "Hammer Strength Row",
            "Seated Cable Row",
        ]
    return [
        "Chest Supported Row",
        "T-Bar Row",
        "Seated Cable Row",
    ]


def _template_slots(template_key: str, req: GeneratePlanRequest) -> Tuple[List[List[str]], List[List[str]]]:
    t = (template_key or "").upper()
    flags = _notes_flags(req)
    avoid_shoulders = flags.get("avoid_shoulders", False)

    if t == "UPPER_A":
        main = [CHEST_COMPOUND, LAT_COMPOUND, CHEST_ISO]
        if avoid_shoulders:
            # replace lateral slot with triceps/abs filler to avoid shoulders
            acc = [_row_pool(req), TRI_SIDES, BICEPS]
        else:
            acc = [_row_pool(req), LATERAL, BICEPS]
        return main, acc

    if t == "UPPER_B":
        main = [_row_pool(req), CHEST_COMPOUND, LAT_COMPOUND]
        if avoid_shoulders:
            # replace rear delt slot with triceps overhead or abs
            acc = [CHEST_ISO, TRI_OVERHEAD, BICEPS]
        else:
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
        if avoid_shoulders:
            # Do not include shoulder presses or laterals; use chest/press + arms + abs
            main = [FLAT_PRESS]
            acc  = [BICEPS, TRI_SIDES, ABS]
        else:
            main = [SHOULDER_PRESS]
            acc  = [LATERAL, BICEPS, BICEPS]
        return main, acc
    
        # -----------------
    # Full Body (FB) templates
    # -----------------
    if t == "FB_A":
        main = [
            CHEST_COMPOUND,      # incline press movement
            LAT_COMPOUND,        # lat pulldown
            UPPER_BACK_ROW,      # upper back row variant
        ]
        acc = [
            LATERAL,
            TRI_OVERHEAD,        # triceps extension
            BICEPS,              # curl variation
            QUAD_COMPOUND,       # squat pattern (hack squat)
            LEG_EXT,
            CALVES,
            ABDUCTOR,
            CABLE_CRUNCH,
        ]
        # If avoiding shoulders, remove lateral raises from accessory pool
        if avoid_shoulders:
            acc = [slot for slot in acc if slot != LATERAL]
        return main, acc

    if t == "FB_B":
        main = [
            UPPER_BACK_ROW,      # upper back row variant
            FLAT_PRESS,          # flat press
            ROW_CLOSE,           # close grip row (lats)
        ]
        acc = [
            TRI_SIDES,           # triceps (medial)
            BICEPS,
            HINGE,               # rdl
            LEG_EXT,
            CALVES,
            ADDUCTOR,
            LATERAL,
        ]
        if avoid_shoulders:
            acc = [slot for slot in acc if slot is not LATERAL]
        return main, acc

    if t == "FB_C":
        main = [
            LAT_COMPOUND,        # lat pulldown
            UPPER_BACK_ROW,      # upper back row
            CHEST_ISO,           # chest fly (pec deck/cable fly)
        ]
        acc = [
            CHEST_COMPOUND,      # incline press
            TRI_OVERHEAD,
            BICEPS,
            QUAD_COMPOUND,       # squat pattern
            LEG_EXT,
            HAM_CURL,
            CALVES,
            CABLE_CRUNCH,
        ]
        return main, acc

    # -----------------
    # 6-day split templates
    # -----------------
    if t == "PUSH":
        main = [
            CHEST_COMPOUND,  # chest press 1
            CHEST_ISO,       # chest fly
        ]
        if avoid_shoulders:
            # remove shoulder slots and replace with triceps/biceps/abs fillers
            acc = [TRI_SIDES, TRI_OVERHEAD, BICEPS, ABS]
        else:
            acc = [
                SHOULDER_PRESS,  # shoulder movement 1
                LATERAL,         # shoulder movement 2 (machine lateral raise exists)
                TRI_SIDES,       # tricep 1
                TRI_OVERHEAD,    # tricep 2
            ]
        return main, acc

    if t == "PULL":
        main = [
            LAT_COMPOUND,    # back 1
            _row_pool(req),  # back 2
            UPPER_BACK_ROW,  # back 3
        ]
        acc = [
            BICEPS,          # biceps 1
            BICEPS,          # biceps 2 (forces variation via banned set)
        ]
        return main, acc

    if t == "CHEST_BACK":
        main = [CHEST_COMPOUND, LAT_COMPOUND]
        acc  = [CHEST_ISO, UPPER_BACK_ROW]
        return main, acc

    if t == "REST":
        return [], []


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
    main_slots, acc_slots = _template_slots(template_key, req)
    acc_slots = list(acc_slots)  # in case it's a tuple
    acc_slots += _triceps_slots_for_day(template_key, has_sharms)
    
    if not main_slots and not acc_slots:
        return

    banned: set[str] = set()

    def build_items(slots: List[List[str]]) -> List[ExerciseItem]:
        items: List[ExerciseItem] = []
        for slot in slots:
            flags = _notes_flags(req)
            pick = _pick_first_valid(
                slot,
                banned=banned,
                prefer_machines=flags["prefer_machines"],
                prefer_cables=flags.get("prefer_cables", False),
            )
            if not pick:
                continue

            # If user asked to avoid shoulders, ensure we don't pick shoulder-dominant moves
            if flags.get("avoid_shoulders", False) and _is_shoulder_dominant(pick):
                alternative = None
                for raw in slot:
                    cand = _pick_first_valid([raw], banned=banned, prefer_machines=flags["prefer_machines"], prefer_cables=flags.get("prefer_cables", False))
                    if cand and not _is_shoulder_dominant(cand):
                        alternative = cand
                        break
                if alternative:
                    pick = alternative
                else:
                    # no safe pick found in this slot
                    continue

            banned.add(normalize_name(pick))
            items.append(
                ExerciseItem(
                    name=pick,
                    sets=1 if template_key.upper().startswith("FB_") else 2,  # your preferred default
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

def _max_total_exercises_for_minutes(session_minutes: int) -> int:
    m = session_minutes or 60
    if m <= 35: return 4   # 2 main + 2 accessories
    if m <= 45: return 5   # 2 main + 3 accessories
    if m <= 60: return 6   # 2 main + 4 accessories
    if m <= 75: return 7   # 2 main + 5 accessories
    return 8               # 2 main + 6 accessories (cap)

def _enforce_time_cap(day, session_minutes: int) -> None:
    max_total = _max_total_exercises_for_minutes(session_minutes)

    # Always keep at least 2 mains (your rule)
    if len(day.main) < 2:
        # if main is short for any reason, don't "solve" here; let existing pad logic handle it
        return

    # If main got too big, trim it but keep 2
    if len(day.main) > 3:
        day.main = day.main[:3]  # optional: keep mains from exploding

    # Now trim accessories to fit max_total
    allowed_accessories = max_total - len(day.main)
    if allowed_accessories < 0:
        allowed_accessories = 0

    if len(day.accessories) > allowed_accessories:
        day.accessories = day.accessories[:allowed_accessories]

def _notes_flags(req) -> dict:
    text = (req.constraints or "").lower()
    avoid_tokens = {str(x).strip().lower() for x in (getattr(req, "avoid", None) or [])}
    # Phase 1 canonical tokens (preferred)
    tokens = set((getattr(req, "constraints_tokens", None) or []) + (getattr(req, "preferences_tokens", None) or []))

    # Support both old natural language ("no barbells") and new token format ("BANS: no_barbells")
    no_dumbbells = (
        ("no_dumbbells" in tokens)
        or bool(re.search(r"\bno\s+dumbbells?\b|\bavoid\s+dumbbells?\b", text))
        or ("no_dumbbells" in text)
    )
    no_barbells = (
        ("no_barbells" in tokens)
        or bool(re.search(r"\bno\s+barbells?\b|\bavoid\s+barbells?\b", text))
        or ("no_barbells" in text)
    )
    prefer_machines = (
        ("prefer_machines" in tokens)
        or bool(re.search(r"\bprefer\s+machines?\b|\bmachines?\s+only\b", text))
        or ("prefer_machines" in text)
    )
    prefer_cables = (
        ("prefer_cables" in tokens)
        or bool(re.search(r"\bprefer\s+cables?\b|\bcables?\s+only\b", text))
        or ("prefer_cables" in text)
    )
    # Prefer req.avoid tokens (explicit avoidance list) but fall back to parsing constraints text
    avoid_shoulders = (
        ("shoulders" in avoid_tokens)
        or ("avoid_shoulders" in avoid_tokens)
        or ("avoid: shoulders" in text)
        or ("avoid_shoulders" in text)
        or bool(re.search(r"\bavoid\s+shoulders?\b", text))
    )


    return {
        "no_dumbbells": no_dumbbells,
        "no_barbells": no_barbells,
        "prefer_machines": prefer_machines,
        "prefer_cables": prefer_cables,
        "avoid_shoulders": avoid_shoulders,
    }


def _pick_replacement(name: str, prefer_machines: bool, no_dumbbells: bool, no_barbells: bool) -> str | None:
    key = (name or "").strip().lower()
    cands = _SWAP.get(key)
    if not cands:
        return None

    # filter out candidates that violate bans (string-level v1)
    filtered = []
    for c in cands:
        lc = c.lower()
        if no_dumbbells and (_DB_PAT.search(lc) or "dumbbell" in lc or " db " in f" {lc} "):
            continue
        if no_barbells and _is_barbell_like(c):
            continue
        filtered.append(c)

    if not filtered:
        return None

    if prefer_machines:
        # prefer machine/cable/smith if present
        for c in filtered:
            lc = c.lower()
            if "machine" in lc or "cable" in lc or "smith" in lc:
                return c

    return filtered[0]

def _enforce_equipment_from_notes(day, req) -> None:
    flags = _notes_flags(req)
    no_db = flags["no_dumbbells"]
    no_bb = flags["no_barbells"]
    prefer_m = flags["prefer_machines"]

    if not (no_db or no_bb or prefer_m):
        return

    def violates(name: str) -> bool:
        n = (name or "").lower()
        if no_db and (_DB_PAT.search(n) or "dumbbell" in n):
            return True
        if no_bb and _is_barbell_like(n):
            return True
        return False

    def process_list(lst):
        out = []
        for ex in lst:
            n = ex.name or ""
            if violates(n):
                repl = _pick_replacement(n, prefer_m, no_db, no_bb)
                if repl:
                    # If avoiding shoulders, don't swap into shoulder-dominant replacements
                    if flags.get("avoid_shoulders", False) and _is_shoulder_dominant(repl):
                        # drop if the only safe replacement is a shoulder movement
                        continue
                    ex.name = repl
                    # keep sets/reps/rest normalization later in pipeline
                    out.append(ex)
                else:
                    # drop if no safe replacement
                    continue
            else:
                # If prefer_machines, optionally "soft bias" by swapping obvious free-weight names
                if prefer_m:
                    repl = _pick_replacement(n, prefer_m, no_db, no_bb)
                    if repl:
                        # avoid swapping into shoulder-dominant moves if user avoids shoulders
                        if flags.get("avoid_shoulders", False) and _is_shoulder_dominant(repl):
                            pass
                        else:
                            ex.name = repl
                out.append(ex)
        return out

    day.main = process_list(day.main)
    day.accessories = process_list(day.accessories)


# -----------------------------
# rules engine
# -----------------------------

def apply_rules_v1(plan: GeneratePlanResponse, req: GeneratePlanRequest) -> GeneratePlanResponse:
    # clamp days (keep your existing behavior)
    effective_days = req.days_per_week
    if effective_days > 6:
        effective_days = 6

    # Decide your split/day templates deterministically
    tpls = _select_day_templates(effective_days)
    has_sharms = "SHARMS" in tpls

    # IMPORTANT: weekly_split must match the template length (tpls may include REST)
    target_len = len(tpls)

    # Trim or pad days to match target_len
    if len(plan.weekly_split) > target_len:
        plan.weekly_split = plan.weekly_split[:target_len]
    elif len(plan.weekly_split) < target_len:
        from copy import deepcopy

        # ensure we have a "shape" to clone
        if not plan.weekly_split:
            # if the model returned zero days, we cannot safely pad without the DayPlan constructor
            return plan

        while len(plan.weekly_split) < target_len:
            blank = deepcopy(plan.weekly_split[0])
            blank.day = f"Day {len(plan.weekly_split) + 1}"
            blank.focus = ""
            blank.warmup = []
            blank.main = []
            blank.accessories = []
            plan.weekly_split.append(blank)



    # per-day enforcement
    for i in range(target_len):
        day = plan.weekly_split[i]
        template_key = tpls[i]
        day.focus = _template_to_focus(template_key)
        if template_key == "REST":
            day.warmup = []
            day.main = []
            day.accessories = []
            continue
        _apply_template(day, req, template_key, has_sharms)
        _enforce_equipment_from_notes(day, req)
        _enforce_prefer_cables(day, req)


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

        if (not template_key.upper().startswith("FB_")) and (template_key != "CHEST_BACK"):
            _trim_or_pad_movements(day, req)
            _dedupe_day(day)
            _enforce_compound_cap(day, req.session_minutes) 
        
        _enforce_avoid_shoulders(day, req)
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
