from models.plans import GeneratePlanRequest, GeneratePlanResponse, DayPlan
from routes.rules.engine import apply_rules_v1, _equipment_allows


def _blank_plan() -> GeneratePlanResponse:
    days = [
        DayPlan(day=f"Day {i+1}", focus="", warmup=[], main=[], accessories=[])
        for i in range(7)
    ]
    return GeneratePlanResponse(title="Test", summary="", weekly_split=days)


def _collect_names(plan: GeneratePlanResponse) -> list[str]:
    names = []
    for d in plan.weekly_split:
        for ex in d.main + d.accessories:
            names.append(ex.name)
    return names


def test_equipment_modes_are_enforced_and_distinct():
    req_full = GeneratePlanRequest(equipment="full_gym")
    req_db = GeneratePlanRequest(equipment="dumbbells")
    req_home = GeneratePlanRequest(equipment="home_gym")
    req_bw = GeneratePlanRequest(equipment="bodyweight")

    plan_full = apply_rules_v1(_blank_plan(), req_full)
    plan_db = apply_rules_v1(_blank_plan(), req_db)
    plan_home = apply_rules_v1(_blank_plan(), req_home)
    plan_bw = apply_rules_v1(_blank_plan(), req_bw)

    for plan, req in [
        (plan_full, req_full),
        (plan_db, req_db),
        (plan_home, req_home),
        (plan_bw, req_bw),
    ]:
        names = _collect_names(plan)
        assert names
        assert all(_equipment_allows(n, req) for n in names)
        assert req.equipment in plan.equipment_note

    assert set(_collect_names(plan_full)) != set(_collect_names(plan_db))
    assert set(_collect_names(plan_db)) != set(_collect_names(plan_bw))
    assert set(_collect_names(plan_home)) != set(_collect_names(plan_bw))
