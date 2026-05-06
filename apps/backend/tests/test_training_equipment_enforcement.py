import re

from models.plans import DayPlan, ExerciseItem, GeneratePlanRequest, GeneratePlanResponse
from routes.rules.engine import (
    _allowed_for_equipment,
    _estimate_day_minutes,
    _is_barbell_like,
    apply_rules_v1,
)


_DB_PAT = re.compile(r"\bdumbbell(s)?\b|\bdb\b", re.I)


def _plan_with_banned_equipment() -> GeneratePlanResponse:
    return GeneratePlanResponse(
        title="Test",
        summary="",
        weekly_split=[
            DayPlan(
                day="Day 1",
                focus="Upper",
                warmup=[],
                main=[
                    ExerciseItem(
                        name="Barbell Bench Press",
                        sets=2,
                        reps="6-8",
                        rest_seconds=240,
                        notes="",
                    ),
                    ExerciseItem(
                        name="Dumbbell Romanian Deadlift",
                        sets=2,
                        reps="6-8",
                        rest_seconds=240,
                        notes="",
                    ),
                ],
                accessories=[
                    ExerciseItem(
                        name="Dumbbell Curl",
                        sets=2,
                        reps="8-12",
                        rest_seconds=180,
                        notes="",
                    )
                ],
            )
        ],
    )


def _collect_names(plan: GeneratePlanResponse) -> list[str]:
    names = []
    for day in plan.weekly_split:
        for exercise in day.main + day.accessories:
            names.append(exercise.name)
    return names


def test_no_barbells_and_no_dumbbells_constraints_are_enforced():
    req = GeneratePlanRequest(constraints="no barbells no dumbbells")

    result = apply_rules_v1(_plan_with_banned_equipment(), req)
    names = _collect_names(result)

    assert names
    assert all(not _is_barbell_like(name) for name in names)
    assert all(not _DB_PAT.search(name) for name in names)


def test_dumbbell_plan_excludes_gym_equipment_for_arm_focus():
    req = GeneratePlanRequest(
        days_per_week=4,
        session_minutes=45,
        equipment="dumbbells",
        focus_muscles=["arms"],
    )

    result = apply_rules_v1(_plan_with_banned_equipment(), req)
    names = _collect_names(result)

    assert names
    assert all(_allowed_for_equipment(name, "dumbbells") for name in names)


def test_bodyweight_plan_excludes_gym_equipment_and_stays_short():
    req = GeneratePlanRequest(
        days_per_week=3,
        session_minutes=30,
        equipment="bodyweight",
        focus_muscles=["legs"],
    )

    result = apply_rules_v1(_plan_with_banned_equipment(), req)

    for day in result.weekly_split:
        names = [exercise.name for exercise in day.main + day.accessories]
        if not names:
            continue
        assert len(names) <= 4
        assert _estimate_day_minutes(day) <= req.session_minutes
        assert all(_allowed_for_equipment(name, "bodyweight") for name in names)
