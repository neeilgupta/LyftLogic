import sqlite3
import threading
from datetime import datetime, timedelta, timezone

import pytest

from deps import get_current_user
from main import app
from services import db
from services.nutrition.generate import (
    _macros_reconciled,
    required_diet_tags_for_user,
)


def make_targets(maintenance: int = 2600):
    return {
        "maintenance": maintenance,
        "cut": {"0.5": maintenance - 250, "1": maintenance - 500, "2": maintenance - 1000},
        "bulk": {"0.5": maintenance + 250, "1": maintenance + 500, "2": maintenance + 1000},
    }


@pytest.fixture()
def temp_db(monkeypatch, tmp_path):
    db_path = tmp_path / "lyftlogic_test.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.init_db()
    return db_path


@pytest.fixture()
def authed_nutrition(monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: {"id": 1, "email": "test@example.com"}
    monkeypatch.setattr(
        db,
        "add_nutrition_plan",
        lambda **kwargs: {
            "id": 1,
            "created_at": "2026-05-02T00:00:00Z",
            "title": kwargs["title"],
            "input_json": kwargs["input_json"],
            "output_json": kwargs["output_json"],
            "owner_id": kwargs["owner_id"],
        },
    )
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def _insert_user_graph(email: str = "phase0@example.com") -> int:
    expires_at = (datetime.now(timezone.utc) + timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    with db._conn() as conn:
        user_id = conn.execute(
            "INSERT INTO users(email, password_hash, email_verified) VALUES (?, ?, 1)",
            (email, "hash"),
        ).lastrowid
        plan_id = conn.execute(
            "INSERT INTO plans(title, input_json, output_json, owner_id) VALUES (?, '{}', '{}', ?)",
            ("Training", user_id),
        ).lastrowid
        conn.execute(
            "INSERT INTO plan_versions(plan_id, version, input_json, output_json, diff_json) VALUES (?, 1, '{}', '{}', '{}')",
            (plan_id,),
        )
        conn.execute(
            "INSERT INTO nutrition_plans(title, input_json, output_json, owner_id) VALUES (?, '{}', '{}', ?)",
            ("Nutrition", user_id),
        )
        conn.execute(
            "INSERT INTO sessions(token, user_id, expires_at) VALUES (?, ?, ?)",
            ("session-token", user_id, expires_at),
        )
        conn.execute(
            "INSERT INTO login_codes(email, code_hash, expires_at) VALUES (?, 'code-hash', ?)",
            (email, expires_at),
        )
        conn.execute(
            "INSERT INTO email_verification_tokens(user_id, token_hash, expires_at) VALUES (?, 'verify-hash', ?)",
            (user_id, expires_at),
        )
        conn.execute(
            "INSERT INTO password_reset_tokens(user_id, token_hash, expires_at) VALUES (?, 'reset-hash', ?)",
            (user_id, expires_at),
        )
        return int(user_id)


def _counts_for_user(user_id: int, email: str = "phase0@example.com") -> dict[str, int]:
    with db._conn() as conn:
        return {
            "users": conn.execute("SELECT COUNT(*) FROM users WHERE id = ?", (user_id,)).fetchone()[0],
            "sessions": conn.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,)).fetchone()[0],
            "login_codes": conn.execute("SELECT COUNT(*) FROM login_codes WHERE email = ?", (email,)).fetchone()[0],
            "email_verification_tokens": conn.execute(
                "SELECT COUNT(*) FROM email_verification_tokens WHERE user_id = ?", (user_id,)
            ).fetchone()[0],
            "password_reset_tokens": conn.execute(
                "SELECT COUNT(*) FROM password_reset_tokens WHERE user_id = ?", (user_id,)
            ).fetchone()[0],
            "plans": conn.execute("SELECT COUNT(*) FROM plans WHERE owner_id = ?", (user_id,)).fetchone()[0],
            "plan_versions": conn.execute(
                "SELECT COUNT(*) FROM plan_versions WHERE plan_id IN (SELECT id FROM plans WHERE owner_id = ?)",
                (user_id,),
            ).fetchone()[0],
            "nutrition_plans": conn.execute(
                "SELECT COUNT(*) FROM nutrition_plans WHERE owner_id = ?", (user_id,)
            ).fetchone()[0],
        }


def test_sqlite_connections_keep_thread_guard(temp_db):
    conn = db._conn()
    errors: list[BaseException] = []

    def use_connection_from_other_thread():
        try:
            conn.execute("SELECT 1")
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(target=use_connection_from_other_thread)
    thread.start()
    thread.join()
    conn.close()

    assert errors
    assert isinstance(errors[0], sqlite3.ProgrammingError)


def test_delete_user_rolls_back_on_mid_delete_failure(temp_db):
    user_id = _insert_user_graph()
    before = _counts_for_user(user_id)

    with db._conn() as conn:
        conn.execute(
            """
            CREATE TRIGGER fail_nutrition_delete
            BEFORE DELETE ON nutrition_plans
            BEGIN
                SELECT RAISE(ABORT, 'forced nutrition delete failure');
            END;
            """
        )

    with pytest.raises(sqlite3.DatabaseError, match="forced nutrition delete failure"):
        db.delete_user(user_id)

    assert _counts_for_user(user_id) == before


def test_delete_user_removes_all_owned_rows(temp_db):
    user_id = _insert_user_graph()

    db.delete_user(user_id)

    assert _counts_for_user(user_id) == {
        "users": 0,
        "sessions": 0,
        "login_codes": 0,
        "email_verification_tokens": 0,
        "password_reset_tokens": 0,
        "plans": 0,
        "plan_versions": 0,
        "nutrition_plans": 0,
    }


def test_required_diet_tags_fail_closed_for_unknown_diets():
    assert required_diet_tags_for_user(None) == set()
    assert required_diet_tags_for_user(" none ") == set()
    assert required_diet_tags_for_user(" vegan ") == {"vegan"}
    assert required_diet_tags_for_user("vegetarian") == {"vegetarian", "vegan"}
    assert required_diet_tags_for_user("pescatarian") == {
        "pescatarian",
        "vegetarian",
        "vegan",
    }

    with pytest.raises(ValueError, match="Unsupported diet"):
        required_diet_tags_for_user("keto")


def test_macro_reconciliation_uses_percentage_tolerance():
    within_5_pct = {"macros": {"protein_g": 100, "carbs_g": 275, "fat_g": 50, "calories": 2000}}
    over_5_pct = {"macros": {"protein_g": 100, "carbs_g": 250, "fat_g": 50, "calories": 2000}}
    unparsable = {"macros": {"protein_g": "bad", "carbs_g": 100, "fat_g": 50, "calories": 2000}}

    assert _macros_reconciled(within_5_pct) is True
    assert _macros_reconciled(over_5_pct) is False
    assert _macros_reconciled(unparsable) is False
    assert _macros_reconciled({"name": "No macro block"}) is True


@pytest.mark.parametrize("diet", ["vegan", "vegetarian", "pescatarian", " Vegan "])
def test_nutrition_generate_accepts_supported_diets(client, authed_nutrition, diet):
    payload = {
        "targets": make_targets(),
        "diet": diet,
        "allergies": [],
        "meals_needed": 2,
        "batch_size": 2,
        "max_attempts": 10,
    }

    response = client.post("/nutrition/generate", json=payload)

    assert response.status_code == 200, response.text
    accepted = response.json()["output"]["accepted"]
    assert len(accepted) == 2

    normalized = diet.strip().lower()
    required = {normalized}
    if normalized == "vegetarian":
        required = {"vegetarian", "vegan"}
    if normalized == "pescatarian":
        required = {"pescatarian", "vegetarian", "vegan"}
    for meal in accepted:
        for ingredient in meal.get("ingredients", []):
            tags = {str(tag).lower() for tag in ingredient.get("diet_tags", [])}
            assert tags & required


@pytest.mark.parametrize("diet", ["keto", "halal", "kosher", "gluten_free", "random_diet", " Keto "])
def test_nutrition_generate_rejects_unsupported_diets(client, authed_nutrition, diet):
    payload = {
        "targets": make_targets(),
        "diet": diet,
        "allergies": [],
        "meals_needed": 2,
        "batch_size": 2,
        "max_attempts": 2,
    }

    response = client.post("/nutrition/generate", json=payload)

    assert response.status_code == 422
    assert "Unsupported diet" in response.text


def test_nutrition_regenerate_accepts_supported_diet(client, authed_nutrition):
    generate_payload = {
        "targets": make_targets(),
        "diet": "vegan",
        "allergies": [],
        "meals_needed": 2,
        "batch_size": 2,
        "max_attempts": 10,
    }
    generated = client.post("/nutrition/generate", json=generate_payload)
    assert generated.status_code == 200, generated.text

    regenerate_payload = {
        "prev_snapshot": generated.json()["version_snapshot"],
        "targets": make_targets(),
        "diet": "pescatarian",
        "allergies": [],
        "meals_needed": 2,
        "batch_size": 2,
        "max_attempts": 10,
    }

    response = client.post("/nutrition/regenerate", json=regenerate_payload)

    assert response.status_code == 200, response.text


@pytest.mark.parametrize("diet", ["keto", "halal", "kosher", "gluten_free", "random_diet", " Keto "])
def test_nutrition_regenerate_rejects_unsupported_diets(client, authed_nutrition, diet):
    payload = {
        "prev_snapshot": {
            "version": 1,
            "targets": make_targets(),
            "accepted_meals": [],
            "rejected_meals": [],
            "constraints_snapshot": {},
        },
        "targets": make_targets(),
        "diet": diet,
        "allergies": [],
        "meals_needed": 2,
        "batch_size": 2,
        "max_attempts": 2,
    }

    response = client.post("/nutrition/regenerate", json=payload)

    assert response.status_code == 422
    assert "Unsupported diet" in response.text
