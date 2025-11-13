
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
    assert resp.json() == {"ok": True}


def test_generate_workout_basic():
    payload = {
        "focus": "upper",
        "equipment": "gym",
        "soreness_text": "no soreness anywhere",
        "use_db_logs": False,
    }
    resp = client.post("/plans/workout", json=payload)
    data = resp.json()

    assert resp.status_code == 200
    assert data["focus"] == "upper"
    assert data["equipment"] == "gym"
    assert isinstance(data["exercises"], list)
    assert len(data["exercises"]) > 0
    # explanation should be a non-empty string now
    assert isinstance(data["explanation"], str)
    assert data["explanation"].strip() != ""


def test_log_and_use_db():
    # 1) log a set
    log_payload = {
        "name": "Barbell Bench Press",
        "reps": 8,
        "weight_kg": 70,
        "rir": 1,
        "focus": "upper",
    }
    resp_log = client.post("/logs/", json=log_payload)
    assert resp_log.status_code == 200
    added = resp_log.json()["added"]
    assert added["name"] == "Barbell Bench Press"

    # 2) generate a plan that can (optionally) use DB logs
    workout_payload = {
        "focus": "upper",
        "equipment": "gym",
        "soreness_text": "no soreness",
        "use_db_logs": True,
    }
    resp_plan = client.post("/plans/workout", json=workout_payload)
    data = resp_plan.json()

    assert resp_plan.status_code == 200
    assert data["focus"] == "upper"
    assert isinstance(data["exercises"], list)
    assert len(data["exercises"]) > 0