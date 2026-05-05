import json

from models.plans import DayPlan, ExerciseItem, GeneratePlanResponse
from services import db
from services.nutrition.versioning import build_nutrition_version_v1, diff_nutrition


def _targets(maintenance: int = 2400) -> dict:
    return {
        "maintenance": maintenance,
        "cut": {"0.5": maintenance - 250, "1": maintenance - 500, "2": maintenance - 1000},
        "bulk": {"0.5": maintenance + 250, "1": maintenance + 500, "2": maintenance + 1000},
    }


def _snapshot(version: int, meals: list[str], maintenance: int = 2400) -> dict:
    return build_nutrition_version_v1(
        version=version,
        targets=_targets(maintenance),
        accepted_meals=[{"name": name} for name in meals],
        rejected_meals=[],
        constraints_snapshot={"diet": None, "allergies": []},
    )


def _plan_output(title: str = "Versioned Plan") -> dict:
    return GeneratePlanResponse(
        title=title,
        summary="",
        weekly_split=[
            DayPlan(
                day="Day 1",
                focus="Upper",
                warmup=[],
                main=[
                    ExerciseItem(name="Chest Press Machine", sets=2, reps="8-12", rest_seconds=180, notes="")
                ],
                accessories=[],
            )
        ],
    ).model_dump()


def test_nutrition_snapshot_builder_is_deterministic():
    meals = [{"name": "Oatmeal"}, {"key": "chicken_rice", "name": "Chicken Rice"}]

    snapshot_1 = build_nutrition_version_v1(
        version=1,
        targets=_targets(),
        accepted_meals=meals,
        rejected_meals=[],
        constraints_snapshot={"diet": None},
    )
    snapshot_2 = build_nutrition_version_v1(
        version=1,
        targets=_targets(),
        accepted_meals=meals,
        rejected_meals=[],
        constraints_snapshot={"diet": None},
    )

    assert snapshot_1 == snapshot_2


def test_diff_detects_meal_replacement_and_addition():
    old_plan = _snapshot(1, ["Oatmeal", "Chicken Rice"])
    new_plan = _snapshot(2, ["Oatmeal", "Turkey Bowl", "Greek Yogurt"])

    diff = diff_nutrition(old_plan, new_plan)

    assert diff["meals_replaced"][0]["from"]["name"] == "Chicken Rice"
    assert diff["meals_replaced"][0]["to"]["name"] == "Turkey Bowl"
    assert diff["meals_added"][0]["meal"]["name"] == "Greek Yogurt"


def test_list_plan_versions_handles_null_diff_json():
    db.init_db()
    saved = db.add_plan(
        title="Null Diff Version",
        input_json=json.dumps({"constraints": ""}),
        output_json=json.dumps(_plan_output()),
        owner_id=1,
    )

    versions = db.list_plan_versions(saved["id"])

    assert versions
    assert versions[0]["diff"] is None


def test_restore_endpoint_returns_exact_previous_snapshot(client):
    original_input = {
        "goal": "hypertrophy",
        "experience": "intermediate",
        "days_per_week": 4,
        "session_minutes": 60,
        "equipment": "full_gym",
        "constraints": "",
        "constraints_tokens": [],
        "preferences_tokens": [],
        "avoid": [],
        "base_constraints_text": "",
        "chat_history": [],
    }
    saved = db.add_plan(
        title="Restore Exact",
        input_json=json.dumps(original_input),
        output_json=json.dumps(_plan_output("Original")),
        owner_id=1,
    )
    db.create_plan_version(
        saved["id"],
        2,
        {**original_input, "constraints_tokens": ["no_barbells"]},
        _plan_output("Changed"),
        diff={"changed": True},
    )

    response = client.post(f"/plans/{saved['id']}/restore", json={"version": 1})

    assert response.status_code == 200, response.text
    restored = response.json()
    assert restored["version"] == 3
    assert restored["input"] == original_input
    assert restored["output"] == _plan_output("Original")
    assert restored["diff"] == {"restored_from": 1}
