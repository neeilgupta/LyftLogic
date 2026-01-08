import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on the Python path so we can import main
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from main import app

client = TestClient(app)

def _requires_openai():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set; skipping tests that require /plans/generate")

_cached_plan_id = None

def _generate_plan_id() -> int:
    _requires_openai()
    payload = {
        "goal": "hypertrophy",
        "experience": "intermediate",
        "days_per_week": 4,
        "session_minutes": 60,
        "equipment": "full_gym",
        "soreness_notes": "no soreness",
        "constraints": "",
    }
    r = client.post("/plans/generate", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "id" in data, data
    return data["id"]

def _get_or_create_plan_id() -> int:
    global _cached_plan_id
    if _cached_plan_id is not None:
        return _cached_plan_id
    _cached_plan_id = _generate_plan_id()
    return _cached_plan_id


def test_health():
    r = client.get("/health")
    assert r.status_code == 200, r.text
    assert r.json() == {"status": "ok"}


def test_generate_plan_basic():
    # This test *requires* OpenAI because it calls /generate
    plan_id = _generate_plan_id()
    assert isinstance(plan_id, int)


def test_edit_and_apply_patch_increments_version():
    plan_id = _get_or_create_plan_id()

    # 1) edit -> proposed_patch
    resp_edit = client.post(f"/plans/{plan_id}/edit", json={"message": "no barbells"})
    assert resp_edit.status_code == 200, resp_edit.text
    edit = resp_edit.json()
    assert edit["can_apply"] is True
    assert "no_barbells" in edit["proposed_patch"]["constraints_add"]

    # 2) apply patch
    resp_apply = client.post(f"/plans/{plan_id}/apply", json=edit["proposed_patch"])
    assert resp_apply.status_code == 200, resp_apply.text
    applied = resp_apply.json()
    assert applied["plan_id"] == plan_id

    # 3) GET plan should show version increment + token stored
    resp_get = client.get(f"/plans/{plan_id}")
    assert resp_get.status_code == 200, resp_get.text
    got = resp_get.json()
    assert got["version"] >= 2
    assert "no_barbells" in (got["input"].get("constraints_tokens") or [])
