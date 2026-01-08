import os
import sys
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


from main import app

client = TestClient(app)

def _maybe_generate_plan_id() -> int:
    """
    Generate a plan only if OPENAI_API_KEY is set.
    Otherwise, skip this integration test cleanly.
    """
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("No OPENAI_API_KEY; skipping integration test that requires /plans/generate")

    payload = {
        "goal": "hypertrophy",
        "experience": "intermediate",
        "days_per_week": 4,
        "session_minutes": 60,
        "equipment": "full_gym",
        "soreness_notes": "",
        "constraints": ""
    }

    r = client.post("/plans/generate", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "id" in data, data
    return data["id"]

def test_edit_apply_chain_three_times():
    plan_id = _maybe_generate_plan_id()

    messages = ["no barbells", "prefer cables", "avoid shoulders"]
    last_version = None

    for i, msg in enumerate(messages):
        # EDIT
        r_edit = client.post(f"/plans/{plan_id}/edit", json={"message": msg})
        assert r_edit.status_code == 200, r_edit.text
        edit = r_edit.json()

        assert edit.get("can_apply") is True, edit
        patch = edit["proposed_patch"]
        assert isinstance(patch, dict), patch

        # APPLY (send patch directly)
        r_apply = client.post(f"/plans/{plan_id}/apply", json=patch)
        assert r_apply.status_code == 200, r_apply.text
        applied = r_apply.json()

        # VERSION monotonic
        assert "version" in applied, applied
        assert isinstance(applied["version"], int), applied["version"]

        if last_version is not None:
            assert applied["version"] == last_version + 1, (last_version, applied["version"])
        last_version = applied["version"]

        # After the 2nd apply, verify earlier constraint still persists
        if i == 1:
            mid = client.get(f"/plans/{plan_id}")
            assert mid.status_code == 200, mid.text
            mid_json = mid.json()

            mid_version = mid_json.get("version")
            assert mid_version == last_version, (mid_version, last_version)

            mid_constraints = (mid_json.get("input", {}).get("constraints_tokens") or [])
            assert "no_barbells" in mid_constraints, mid_constraints

    # FINAL STATE assertions
    r_final = client.get(f"/plans/{plan_id}")
    assert r_final.status_code == 200, r_final.text
    final = r_final.json()

    inp = final.get("input", {})
    constraints_tokens = inp.get("constraints_tokens") or []
    preferences_tokens = inp.get("preferences_tokens") or []
    avoid = inp.get("avoid") or []

    # CUMULATIVE persistence checks
    assert "no_barbells" in constraints_tokens, constraints_tokens
    assert "prefer_cables" in preferences_tokens, preferences_tokens

    # Pick whichever representation your parser uses
    assert ("avoid_shoulders" in avoid) or ("shoulders" in avoid), avoid
    # Enable these only if your parser supports them today
    # assert "prefer_cables" in preferences_tokens, preferences_tokens
    # assert "avoid_shoulders" in avoid or "shoulders" in avoid, avoid

    # Leakage smoke test (tune strings to your naming conventions)
    names = [n.lower() for n in _all_exercise_names(final.get("output", {}))]
    assert not any("barbell" in n for n in names), names

def _all_exercise_names(plan_output: dict) -> list[str]:
    names = []
    if not isinstance(plan_output, dict):
        return names
    days = plan_output.get("days") or []
    for d in days:
        for ex in (d.get("main") or []):
            if isinstance(ex, dict) and ex.get("name"):
                names.append(ex["name"])
        for ex in (d.get("accessories") or []):
            if isinstance(ex, dict) and ex.get("name"):
                names.append(ex["name"])
    return names