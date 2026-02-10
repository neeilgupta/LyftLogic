from routes.rules.engine import _estimate_day_minutes, _enforce_session_minutes
from models.plans import DayPlan, ExerciseItem, GeneratePlanRequest


def _make_day() -> DayPlan:
    return DayPlan(
        day="Day 1",
        focus="Upper",
        warmup=["Optional band warmup"],
        main=[
            ExerciseItem(name="Barbell Bench Press", sets=3, reps="6-8", rest_seconds=240, notes=""),
            ExerciseItem(name="Seated Cable Row", sets=3, reps="6-8", rest_seconds=240, notes=""),
        ],
        accessories=[
            ExerciseItem(name="Lateral Raises", sets=3, reps="8-12", rest_seconds=180, notes=""),
            ExerciseItem(name="Cable Curl", sets=3, reps="8-12", rest_seconds=180, notes=""),
            ExerciseItem(name="Triceps Pushdown", sets=3, reps="8-12", rest_seconds=180, notes=""),
        ],
    )


def test_enforce_session_minutes_reduces_overage():
    day = _make_day()
    req = GeneratePlanRequest(session_minutes=35)

    before = _estimate_day_minutes(day)
    _enforce_session_minutes(day, req)
    after = _estimate_day_minutes(day)

    assert before > req.session_minutes
    assert after <= req.session_minutes
    assert len(day.accessories) <= 3


def test_enforce_session_minutes_adds_volume_under_target():
    day = DayPlan(
        day="Day 1",
        focus="Upper",
        warmup=[],
        main=[
            ExerciseItem(name="Barbell Bench Press", sets=2, reps="6-8", rest_seconds=240, notes=""),
            ExerciseItem(name="Seated Cable Row", sets=2, reps="6-8", rest_seconds=240, notes=""),
        ],
        accessories=[
            ExerciseItem(name="Lateral Raises", sets=1, reps="8-12", rest_seconds=180, notes=""),
            ExerciseItem(name="Cable Curl", sets=1, reps="8-12", rest_seconds=180, notes=""),
        ],
    )

    req = GeneratePlanRequest(session_minutes=90)
    before_sets = [ex.sets for ex in day.accessories]
    _enforce_session_minutes(day, req)
    after_sets = [ex.sets for ex in day.accessories]

    assert sum(after_sets) >= sum(before_sets)
