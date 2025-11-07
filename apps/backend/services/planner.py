# apps/backend/services/planner.py
"""
Workout Planning Service

This module handles the core logic for generating workout plans, including:
- Exercise selection based on body focus (upper/lower/full)
- Equipment-based exercise substitutions
- Progressive overload calculations
- Soreness management
- Weekly training schedule optimization
"""

from datetime import date

# Template workouts for different body focuses
# Each exercise includes default sets/reps based on common strength training protocols
BASE_EXERCISES = {
    "upper": [  # Upper body focused workout
        {"name": "Barbell Bench Press", "sets": 3, "reps": 6},  # Primary push
        {"name": "Barbell Row",         "sets": 3, "reps": 8},  # Primary pull
        {"name": "Overhead Press",      "sets": 3, "reps": 6},  # Secondary push
        {"name": "Lat Pulldown",        "sets": 3, "reps": 10}, # Secondary pull
    ],
    "lower": [
        {"name": "Back Squat",          "sets": 3, "reps": 5},
        {"name": "Romanian Deadlift",   "sets": 3, "reps": 8},
        {"name": "Leg Press",           "sets": 3, "reps": 10},
        {"name": "Calf Raise",          "sets": 3, "reps": 12},
    ],
    "full": [
        {"name": "Front Squat",         "sets": 3, "reps": 5},
        {"name": "Bench Press",         "sets": 3, "reps": 6},
        {"name": "Row",                 "sets": 3, "reps": 8},
    ],
}

DUMBBELL_ALTS = {
    "Barbell Bench Press": "DB Bench Press",
    "Barbell Row": "DB Row",
    "Overhead Press": "DB Overhead Press",
    "Back Squat": "Goblet Squat",
    "Romanian Deadlift": "DB Romanian Deadlift",
    "Leg Press": "DB Split Squat",
    "Front Squat": "Goblet Squat",
    "Bench Press": "DB Bench Press",
    "Row": "DB Row",
}

BAND_OR_BW_ALTS = {
    "Barbell Bench Press": "Push-ups",
    "Barbell Row": "Inverted Rows",
    "Overhead Press": "Pike Push-ups",
    "Back Squat": "Bodyweight Squat",
    "Romanian Deadlift": "Hip Hinge (BW)",
    "Leg Press": "Step-ups",
    "Front Squat": "Bodyweight Squat",
    "Bench Press": "Push-ups",
    "Row": "Inverted Rows",
    "Lat Pulldown": "Band Pulldown",
    "Calf Raise": "Single-leg Calf Raise",
}

SORENESS_MAP = {
    "triceps": ["Bench Press","Overhead Press","DB Bench Press","DB Overhead Press","Push-ups","Dips"],
    "quads":   ["Back Squat","Front Squat","Leg Press","Goblet Squat","Split Squat","Step-ups"],
    "hamstrings": ["Romanian Deadlift","DB Romanian Deadlift","Hip Hinge (BW)"],
    "chest": ["Bench Press","DB Bench Press","Push-ups","Barbell Bench Press"],
}

def progressive_overload(last_sets):
    """Calculate suggested weight increase based on previous performance.
    
    Args:
        last_sets: List of previous sets with RIR (Reps In Reserve) data
                  Example: [{"reps": 8, "weight_kg": 60, "rir": 2}, ...]
    
    Returns:
        float: Recommended weight increase in kg/lb
               - 2.5 if RIR >= 2 (exercise was too easy)
               - 1.0 if 0 < RIR < 2 (appropriate challenge)
               - 0.0 if RIR <= 0 (exercise was too hard)
    
    RIR (Reps In Reserve) is a measure of how many more reps could have been done.
    Higher RIR means the weight was too light and should be increased more.
    """
    if not last_sets:
        return 0.0
    avg_rir = sum(max(0, s.get("rir", 0)) for s in last_sets) / len(last_sets)
    if avg_rir >= 2: return 2.5  # Significant increase - exercise was too easy
    if avg_rir <= 0: return 0.0  # No increase - exercise was challenging enough
    return 1.0  # Moderate increase - appropriate progression

def _apply_equipment(blocks, equipment: str):
    if equipment == "gym":
        return blocks
    out = []
    for b in blocks:
        name = b["name"]
        if equipment == "dumbbells":
            alt = DUMBBELL_ALTS.get(name, name)
        else:
            alt = BAND_OR_BW_ALTS.get(name, name)
        out.append({**b, "name": alt})
    return out

def adjust_for_soreness(blocks, soreness):
    if not soreness:
        return blocks
    out = []
    for b in blocks:
        aggravated = any(b["name"] in SORENESS_MAP.get(m, []) and lvl >= 3
                         for m, lvl in soreness.items())
        out.append({**b, "name": f"Light {b['name']} (reduce load 20%)"} if aggravated else b)
    return out

def select_blocks(focus: str):
    return BASE_EXERCISES.get(focus, [])

def focus_sequence_for_days(days_per_week: int):
    if days_per_week <= 2: return ["upper","lower"][:days_per_week]
    if days_per_week == 3: return ["full","full","full"]
    if days_per_week == 4: return ["upper","lower","upper","lower"]
    if days_per_week == 5: return ["upper","lower","full","upper","lower"]
    return ["upper","lower","upper","lower","upper","lower"]

def build_workout_plan(focus, last_log_by_ex, soreness=None, equipment="gym"):
    base = _apply_equipment(select_blocks(focus), equipment)
    planned = []
    for b in base:
        last = last_log_by_ex.get(b["name"], [])
        delta = progressive_overload(last)
        planned.append({**b, "weight_delta": delta})
    planned = adjust_for_soreness(planned, soreness)
    return {"date": str(date.today()), "focus": focus, "equipment": equipment, "exercises": planned}

def build_week_plan(days_per_week, last_log_by_ex, soreness=None, equipment="gym"):
    seq = focus_sequence_for_days(days_per_week)
    week = []
    for day_idx, focus in enumerate(seq, start=1):
        d = build_workout_plan(focus, last_log_by_ex, soreness, equipment)
        d["day"] = day_idx
        week.append(d)
    return {"days": days_per_week, "schedule": seq, "plans": week}
