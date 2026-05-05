import json

from fastapi.testclient import TestClient

from deps import get_current_user, get_optional_current_user
from main import app
from models.plans import DayPlan, ExerciseItem, GeneratePlanRequest, GeneratePlanResponse
from routes.rules.engine import apply_rules_v1
from services import db


def _base_input() -> dict:
    req = GeneratePlanRequest(
        goal="hypertrophy",
        experience="intermediate",
        days_per_week=4,
        session_minutes=60,
        equipment="full_gym",
        soreness_notes="",
        constraints="",
    )
    data = req.model_dump()
    data.update(
        {
            "constraints_tokens": [],
            "preferences_tokens": [],
            "avoid": [],
            "emphasis": None,
            "set_style": None,
            "rep_style": None,
            "base_constraints_text": "",
            "chat_history": [],
        }
    )
    return data


def _seed_output() -> dict:
    plan = GeneratePlanResponse(
        title="Offline Phase 1 Plan",
        summary="Seeded without OpenAI.",
        weekly_split=[
            DayPlan(
                day="Day 1",
                focus="Upper",
                warmup=[],
                main=[
                    ExerciseItem(name="Barbell Bench Press", sets=3, reps="6-8", rest_seconds=240, notes=""),
                    ExerciseItem(name="Barbell Row", sets=3, reps="6-8", rest_seconds=240, notes=""),
                ],
                accessories=[
                    ExerciseItem(name="Dumbbell Curl", sets=2, reps="8-12", rest_seconds=180, notes="")
                ],
            )
        ],
    )
    req = GeneratePlanRequest(**{k: _base_input()[k] for k in GeneratePlanRequest.model_fields.keys()})
    return apply_rules_v1(plan=plan, req=req).model_dump()


def _seed_plan(owner_id: int = 1) -> int:
    db.init_db()
    with db._conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users(id, email, password_hash, email_verified)
            VALUES (?, ?, 'test-hash', 1)
            """,
            (owner_id, f"phase1-{owner_id}@example.com"),
        )
    saved = db.add_plan(
        title="Offline Phase 1 Plan",
        input_json=json.dumps(_base_input()),
        output_json=json.dumps(_seed_output()),
        owner_id=owner_id,
    )
    return saved["id"]


def _client_for_user(user_id: int = 1) -> TestClient:
    test_user = {"id": user_id, "email": f"phase1-{user_id}@example.com"}
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_optional_current_user] = lambda: test_user
    return TestClient(app)


def test_edit_apply_chain_three_times_offline():
    plan_id = _seed_plan(owner_id=1)

    try:
        client = _client_for_user(1)

        r0 = client.get(f"/plans/{plan_id}")
        assert r0.status_code == 200, r0.text
        v0 = r0.json()["version"]
        assert v0 == 1

        original_versions = client.get(f"/plans/{plan_id}/versions").json()["items"]
        original_v1 = next(v for v in original_versions if v["version"] == 1)

        messages = ["no barbells", "prefer cables", "avoid shoulders"]
        last_version = v0

        for msg in messages:
            r_edit = client.post(f"/plans/{plan_id}/edit", json={"message": msg})
            assert r_edit.status_code == 200, r_edit.text
            edit = r_edit.json()

            assert edit["can_apply"] is True, edit
            patch = edit["proposed_patch"]
            assert isinstance(patch, dict), patch

            r_apply = client.post(f"/plans/{plan_id}/apply", json=patch)
            assert r_apply.status_code == 200, r_apply.text
            applied = r_apply.json()

            assert applied["version"] == last_version + 1
            last_version = applied["version"]

        r_final = client.get(f"/plans/{plan_id}")
        assert r_final.status_code == 200, r_final.text
        final = r_final.json()

        assert final["version"] == v0 + 3

        inp = final["input"]
        chat = inp["chat_history"]
        assert len(chat) == 3
        assert all({"message", "patch", "created_at"} <= set(item) for item in chat)
        assert [item["message"] for item in chat] == messages

        assert "no_barbells" in inp["constraints_tokens"]
        assert "prefer_cables" in inp["preferences_tokens"]
        assert "shoulders" in inp["avoid"]

        names = [name.lower() for name in _all_exercise_names(final["output"])]
        assert names
        assert not any("barbell" in name for name in names)

        versions = client.get(f"/plans/{plan_id}/versions").json()["items"]
        assert [v["version"] for v in versions] == [4, 3, 2, 1]
        persisted_v1 = next(v for v in versions if v["version"] == 1)
        assert persisted_v1["input"] == original_v1["input"]
        assert persisted_v1["output"] == original_v1["output"]
    finally:
        app.dependency_overrides.clear()


def _all_exercise_names(plan_output: dict) -> list[str]:
    names: list[str] = []
    for day in plan_output.get("weekly_split", []) or []:
        for exercise in (day.get("main") or []) + (day.get("accessories") or []):
            if isinstance(exercise, dict) and exercise.get("name"):
                names.append(exercise["name"])
    return names
