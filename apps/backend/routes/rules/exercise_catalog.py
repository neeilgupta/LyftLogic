"""
Curated exercise universe for LyftLogic.

Only exercises in this catalog may be used for deterministic padding or
replacement. Everything is classified as either "compound" or "isolation".

(Names sourced from the attached Compound/Isolation PDFs.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

KIND_COMPOUND = "compound"
KIND_ISOLATION = "isolation"


@dataclass(frozen=True)
class ExerciseMeta:
    name: str
    kind: str  # "compound" | "isolation"
    region: str  # "upper" | "lower"
    tags: Tuple[str, ...] = ()


# -----------------------------
# Curated catalog
# -----------------------------

EXERCISES: Dict[str, ExerciseMeta] = {
    # ---- Compounds (Upper) ----
    "Barbell Bench Press": ExerciseMeta("Barbell Bench Press", KIND_COMPOUND, "upper", ("chest", "push")),
    "Incline Bench Press": ExerciseMeta("Incline Bench Press", KIND_COMPOUND, "upper", ("chest", "push")),
    "Chest Press": ExerciseMeta("Chest Press", KIND_COMPOUND, "upper", ("chest", "push", "machine")),

    "Lat Pulldown": ExerciseMeta("Lat Pulldown", KIND_COMPOUND, "upper", ("lats", "pull")),
    "Pull Ups": ExerciseMeta("Pull Ups", KIND_COMPOUND, "upper", ("lats", "pull", "bodyweight")),
    "T-Bar Row": ExerciseMeta("T-Bar Row", KIND_COMPOUND, "upper", ("back", "pull")),
    "Chest Supported Rows": ExerciseMeta("Chest Supported Rows", KIND_COMPOUND, "upper", ("back", "pull")),
    "Bent-Over Barbell Rows": ExerciseMeta("Bent-Over Barbell Rows", KIND_COMPOUND, "upper", ("back", "pull", "barbell")),
    "Seated Cable Row": ExerciseMeta("Seated Cable Row", KIND_COMPOUND, "upper", ("back", "pull", "cable")),
    "Single Arm Dumbbell Rows": ExerciseMeta("Single Arm Dumbbell Rows", KIND_COMPOUND, "upper", ("back", "pull", "dumbbell")),

    "Machine Shoulder Press": ExerciseMeta("Machine Shoulder Press", KIND_COMPOUND, "upper", ("shoulders", "push", "machine")),
    "Dumbbell Shoulder Press": ExerciseMeta("Dumbbell Shoulder Press", KIND_COMPOUND, "upper", ("shoulders", "push", "dumbbell")),
    "Overhead Press": ExerciseMeta("Overhead Press", KIND_COMPOUND, "upper", ("shoulders", "push", "barbell")),

    # ---- Compounds (Lower) ----
    "Hack Squat": ExerciseMeta("Hack Squat", KIND_COMPOUND, "lower", ("quads",)),
    "Barbell Back Squat": ExerciseMeta("Barbell Back Squat", KIND_COMPOUND, "lower", ("quads", "barbell")),
    "Leg Press": ExerciseMeta("Leg Press", KIND_COMPOUND, "lower", ("quads", "machine")),
    "Bulgarian Split Squat": ExerciseMeta("Bulgarian Split Squat", KIND_COMPOUND, "lower", ("quads", "glutes")),
    "Romanian Deadlift": ExerciseMeta("Romanian Deadlift", KIND_COMPOUND, "lower", ("hamstrings", "hinge")),
    "Hip Thrust": ExerciseMeta("Hip Thrust", KIND_COMPOUND, "lower", ("glutes",)),

    # ---- Isolations (Lower) ----
    "Leg Extension": ExerciseMeta("Leg Extension", KIND_ISOLATION, "lower", ("quads",)),
    "Sissy Squats": ExerciseMeta("Sissy Squats", KIND_ISOLATION, "lower", ("quads",)),

    "Seated Leg Curl": ExerciseMeta("Seated Leg Curl", KIND_ISOLATION, "lower", ("hamstrings",)),
    "Lying Leg Curl": ExerciseMeta("Lying Leg Curl", KIND_ISOLATION, "lower", ("hamstrings",)),

    "Cable Kickbacks": ExerciseMeta("Cable Kickbacks", KIND_ISOLATION, "lower", ("glutes",)),
    "Machine Hip Abduction": ExerciseMeta("Machine Hip Abduction", KIND_ISOLATION, "lower", ("glutes", "abductors")),
    "Smith Machine Kickbacks": ExerciseMeta("Smith Machine Kickbacks", KIND_ISOLATION, "lower", ("glutes",)),

    "Adductor Machine": ExerciseMeta("Adductor Machine", KIND_ISOLATION, "lower", ("adductors",)),
    "Abductor Machine": ExerciseMeta("Abductor Machine", KIND_ISOLATION, "lower", ("abductors",)),

    "Standing Calf Raise": ExerciseMeta("Standing Calf Raise", KIND_ISOLATION, "lower", ("calves",)),
    "Lever Seated Rotary Calf": ExerciseMeta("Lever Seated Rotary Calf", KIND_ISOLATION, "lower", ("calves",)),
    "Seated Calf Raise": ExerciseMeta("Seated Calf Raise", KIND_ISOLATION, "lower", ("calves",)),

    # ---- Isolations (Back/Chest/Shoulders) ----
    "Straight-Arm Pulldown": ExerciseMeta("Straight-Arm Pulldown", KIND_ISOLATION, "upper", ("lats",)),
    "Single-Arm Cable Pulldown": ExerciseMeta("Single-Arm Cable Pulldown", KIND_ISOLATION, "upper", ("lats",)),
    "Machine Pullover": ExerciseMeta("Machine Pullover", KIND_ISOLATION, "upper", ("lats",)),

    "Reverse Pec Deck": ExerciseMeta("Reverse Pec Deck", KIND_ISOLATION, "upper", ("rear_delts", "upper_back")),
    "Chest-Supported Rear Delt Row": ExerciseMeta("Chest-Supported Rear Delt Row", KIND_ISOLATION, "upper", ("rear_delts", "upper_back")),
    "Cable High Row": ExerciseMeta("Cable High Row", KIND_ISOLATION, "upper", ("upper_back",)),

    "Pec Deck": ExerciseMeta("Pec Deck", KIND_ISOLATION, "upper", ("chest",)),
    "Cable Fly": ExerciseMeta("Cable Fly", KIND_ISOLATION, "upper", ("chest",)),
    "Single-Arm Cable Press-Fly Hybrid": ExerciseMeta("Single-Arm Cable Press-Fly Hybrid", KIND_ISOLATION, "upper", ("chest",)),

    "Front Raises": ExerciseMeta("Front Raises", KIND_ISOLATION, "upper", ("front_delts",)),
    "Machine Lateral Raises": ExerciseMeta("Machine Lateral Raises", KIND_ISOLATION, "upper", ("side_delts",)),
    "Cable Lateral Raises": ExerciseMeta("Cable Lateral Raises", KIND_ISOLATION, "upper", ("side_delts",)),
    "Lateral Raises": ExerciseMeta("Lateral Raises", KIND_ISOLATION, "upper", ("side_delts",)),

    "Rear Delt Fly": ExerciseMeta("Rear Delt Fly", KIND_ISOLATION, "upper", ("rear_delts",)),
    "Cable Rear Delt Fly": ExerciseMeta("Cable Rear Delt Fly", KIND_ISOLATION, "upper", ("rear_delts",)),
    "Face Pull": ExerciseMeta("Face Pull", KIND_ISOLATION, "upper", ("rear_delts", "upper_back")),

    # ---- Isolations (Arms) ----
    "Preacher Curl": ExerciseMeta("Preacher Curl", KIND_ISOLATION, "upper", ("biceps",)),
    "Incline Dumbbell Curl": ExerciseMeta("Incline Dumbbell Curl", KIND_ISOLATION, "upper", ("biceps",)),
    "EZ Barbell Curl": ExerciseMeta("EZ Barbell Curl", KIND_ISOLATION, "upper", ("biceps",)),
    "Cable Curl": ExerciseMeta("Cable Curl", KIND_ISOLATION, "upper", ("biceps",)),
    "Concentration Curl": ExerciseMeta("Concentration Curl", KIND_ISOLATION, "upper", ("biceps",)),

    "Triceps Pushdown": ExerciseMeta("Triceps Pushdown", KIND_ISOLATION, "upper", ("triceps",)),
    "JM Press": ExerciseMeta("JM Press", KIND_ISOLATION, "upper", ("triceps",)),
    "Overhead Triceps Extension": ExerciseMeta("Overhead Triceps Extension", KIND_ISOLATION, "upper", ("triceps",)),
    "Single-Arm Cable Extension": ExerciseMeta("Single-Arm Cable Extension", KIND_ISOLATION, "upper", ("triceps",)),
    "Skull Crushers": ExerciseMeta("Skull Crushers", KIND_ISOLATION, "upper", ("triceps",)),

    # ---- Isolations (Abs/Core) ----
    "Machine Crunch": ExerciseMeta("Machine Crunch", KIND_ISOLATION, "upper", ("abs",)),
    "Cable Crunch": ExerciseMeta("Cable Crunch", KIND_ISOLATION, "upper", ("abs",)),
    "Hanging Leg Raises": ExerciseMeta("Hanging Leg Raises", KIND_ISOLATION, "upper", ("abs",)),
}


# -----------------------------
# Helpers
# -----------------------------

def normalize_name(name: str) -> str:
    """Normalize a name for lookups (keep intentionally simple)."""
    return (name or "").strip()


def is_compound(name: str) -> bool:
    meta = EXERCISES.get(normalize_name(name))
    return bool(meta and meta.kind == KIND_COMPOUND)


def is_isolation(name: str) -> bool:
    meta = EXERCISES.get(normalize_name(name))
    return bool(meta and meta.kind == KIND_ISOLATION)


def all_compounds() -> List[str]:
    return [m.name for m in EXERCISES.values() if m.kind == KIND_COMPOUND]


def all_isolations() -> List[str]:
    return [m.name for m in EXERCISES.values() if m.kind == KIND_ISOLATION]


def get_compounds_for_focus(focus: str) -> List[str]:
    f = (focus or "").lower()
    want_lower = ("lower" in f) or ("leg" in f)
    region = "lower" if want_lower else "upper"
    return [m.name for m in EXERCISES.values() if m.kind == KIND_COMPOUND and m.region == region]


def get_isolations_for_focus(focus: str) -> List[str]:
    f = (focus or "").lower()
    want_lower = ("lower" in f) or ("leg" in f)
    region = "lower" if want_lower else "upper"
    return [m.name for m in EXERCISES.values() if m.kind == KIND_ISOLATION and m.region == region]
