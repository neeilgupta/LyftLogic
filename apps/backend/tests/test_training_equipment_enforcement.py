import re

from models.plans import DayPlan, ExerciseItem, GeneratePlanRequest, GeneratePlanResponse
from routes.rules.engine import _is_barbell_like, apply_rules_v1


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
