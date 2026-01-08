
import os
import sys

# Ensure backend root is on the Python path so we can import main
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}



def test_generate_plan_basic():
    payload = {
        "goal": "hypertrophy",
        "experience": "intermediate",
        "days_per_week": 4,
        "session_minutes": 60,
        "equipment": "full_gym",
        "soreness_notes": "no soreness",
        "constraints": "",
    }
    resp = client.post("/plans/generate", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "id" in data
    assert "title" in data
    assert "weekly_split" in data
    assert isinstance(data["weekly_split"], list)


def test_edit_and_apply_patch_increments_version():
    # 1) generate a plan
    payload = {
        "goal": "hypertrophy",
        "experience": "intermediate",
        "days_per_week": 4,
        "session_minutes": 60,
        "equipment": "full_gym",
        "soreness_notes": "no soreness",
        "constraints": "",
    }
    resp = client.post("/plans/generate", json=payload)
    assert resp.status_code == 200
    plan = resp.json()
    plan_id = plan["id"]

    # 2) edit -> proposed_patch
    resp_edit = client.post(f"/plans/{plan_id}/edit", json={"message": "no barbells"})
    assert resp_edit.status_code == 200
    edit = resp_edit.json()
    assert edit["can_apply"] is True
    assert "no_barbells" in edit["proposed_patch"]["constraints_add"]

    # 3) apply patch
    resp_apply = client.post(f"/plans/{plan_id}/apply", json=edit["proposed_patch"])
    assert resp_apply.status_code == 200
    applied = resp_apply.json()
    assert applied["plan_id"] == plan_id

    # 4) GET plan should show version increment + token stored
    resp_get = client.get(f"/plans/{plan_id}")
    assert resp_get.status_code == 200
    got = resp_get.json()
    assert got["version"] >= 2
    assert "no_barbells" in (got["input"].get("constraints_tokens") or [])
