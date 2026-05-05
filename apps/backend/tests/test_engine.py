from copy import deepcopy

from models.plans import DayPlan, ExerciseItem, GeneratePlanRequest, GeneratePlanResponse
from routes.rules.engine import _estimate_day_minutes, _is_barbell_like, apply_rules_v1


def _exercise(name: str, *, sets: int = 3, reps: str = "8-12", rest: int = 180) -> ExerciseItem:
    return ExerciseItem(name=name, sets=sets, reps=reps, rest_seconds=rest, notes="")


def _base_plan() -> GeneratePlanResponse:
    return GeneratePlanResponse(
        title="Engine Invariant Plan",
        summary="",
        weekly_split=[
            DayPlan(
                day="Day 1",
                focus="Upper",
                warmup=[],
                main=[
                    _exercise("Barbell Bench Press", reps="6-8", rest=240),
                    _exercise("Barbell Row", reps="6-8", rest=240),
                ],
                accessories=[
                    _exercise("Dumbbell Curl"),
                    _exercise("Dumbbell Curl"),
                    _exercise("Lateral Raises"),
                ],
            ),
            DayPlan(
                day="Day 2",
                focus="Lower",
                warmup=[],
                main=[
                    _exercise("Barbell Back Squat", reps="6-8", rest=240),
                    _exercise("Romanian Deadlift", reps="6-8", rest=240),
                ],
                accessories=[_exercise("Leg Curl"), _exercise("Calf Raise")],
            ),
        ],
    )


def _all_exercises(plan: GeneratePlanResponse):
    for day in plan.weekly_split:
        for exercise in day.main + day.accessories:
            yield day, exercise


def test_engine_is_idempotent_for_same_input():
    req = GeneratePlanRequest(days_per_week=4, session_minutes=60)

    result_1 = apply_rules_v1(deepcopy(_base_plan()), req).model_dump()
    result_2 = apply_rules_v1(deepcopy(_base_plan()), req).model_dump()

    assert result_1 == result_2


def test_no_barbells_removes_all_barbell_exercises():
    req = GeneratePlanRequest(days_per_week=4, session_minutes=60, constraints="no barbells")

    result = apply_rules_v1(deepcopy(_base_plan()), req)

    assert [exercise.name for _, exercise in _all_exercises(result)]
    assert all(not _is_barbell_like(exercise.name) for _, exercise in _all_exercises(result))


def test_session_time_within_budget():
    req = GeneratePlanRequest(days_per_week=4, session_minutes=45)

    result = apply_rules_v1(deepcopy(_base_plan()), req)

    for day in result.weekly_split:
        if day.main or day.accessories:
            assert _estimate_day_minutes(day) <= int(req.session_minutes * 1.1)


def test_no_duplicate_exercises_per_day():
    req = GeneratePlanRequest(days_per_week=4, session_minutes=60)

    result = apply_rules_v1(deepcopy(_base_plan()), req)

    for day in result.weekly_split:
        names = [exercise.name.lower() for exercise in day.main + day.accessories]
        assert len(names) == len(set(names))


def test_focus_muscles_prioritize_matching_exercises_when_supported():
    req = GeneratePlanRequest(days_per_week=4, session_minutes=60, focus_muscles=["chest"])

    result = apply_rules_v1(deepcopy(_base_plan()), req)

    upper_days = [day for day in result.weekly_split if "upper" in day.focus.lower()]
    assert upper_days
    assert any("press" in day.main[0].name.lower() or "chest" in day.main[0].name.lower() for day in upper_days)


def test_glute_focus_leg_day_starts_with_glute_pattern():
    req = GeneratePlanRequest(days_per_week=4, session_minutes=60, focus_muscles=["glutes"])

    result = apply_rules_v1(deepcopy(_base_plan()), req)

    leg_days = [day for day in result.weekly_split if "leg" in day.focus.lower()]
    assert leg_days
    assert any("hip thrust" in day.main[0].name.lower() or "glute" in day.main[0].name.lower() for day in leg_days if day.main)


def test_hamstring_day_includes_squat_or_hinge_pattern():
    req = GeneratePlanRequest(days_per_week=4, session_minutes=60, focus_muscles=["hamstrings"])

    result = apply_rules_v1(deepcopy(_base_plan()), req)

    lower_days = [day for day in result.weekly_split if "ham" in day.focus.lower() or "lower" in day.focus.lower()]
    assert lower_days
    names = [exercise.name.lower() for day in lower_days for exercise in day.main + day.accessories]
    assert any("squat" in name or "deadlift" in name or "rdl" in name or "leg curl" in name for name in names)


def test_constraint_ordering_keeps_banned_equipment_out_during_padding():
    req = GeneratePlanRequest(days_per_week=6, session_minutes=60, constraints="no barbells")

    result = apply_rules_v1(deepcopy(_base_plan()), req)

    assert len(result.weekly_split) >= 6
    assert all(not _is_barbell_like(exercise.name) for _, exercise in _all_exercises(result))
