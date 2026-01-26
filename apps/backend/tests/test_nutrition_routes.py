def make_targets(maintenance: int):
    return {
        "maintenance": maintenance,
        "cut": {"0.5": maintenance - 250, "1": maintenance - 500, "2": maintenance - 1000},
        "bulk": {"0.5": maintenance + 250, "1": maintenance + 500, "2": maintenance + 1000},
    }


def test_nutrition_generate_returns_snapshot(client):
    req = {
        "targets": make_targets(2600),
        "diet": None,
        "allergies": [],
        "meals_needed": 2,
        "max_attempts": 1,
        "batch_size": 2,
    }

    r = client.post("/nutrition/generate", json=req)
    assert r.status_code == 200

    body = r.json()
    assert "version_snapshot" in body
    assert body["version_snapshot"]["version"] == 1
    assert body["version_snapshot"]["targets"]["maintenance"] == 2600
    assert len(body["version_snapshot"]["accepted_meals"]) == 2


def test_nutrition_regenerate_returns_diff_and_explanations(client):
    gen_req = {
        "targets": make_targets(2600),
        "diet": None,
        "allergies": [],
        "meals_needed": 2,
        "max_attempts": 1,
        "batch_size": 2,
    }

    r1 = client.post("/nutrition/generate", json=gen_req)
    assert r1.status_code == 200
    prev_snapshot = r1.json()["version_snapshot"]

    regen_req = {
        "prev_snapshot": prev_snapshot,
        "targets": make_targets(2400),  # force a calories diff
        "diet": None,
        "allergies": [],
        "meals_needed": 2,
        "max_attempts": 1,
        "batch_size": 2,
    }

    r2 = client.post("/nutrition/regenerate", json=regen_req)
    assert r2.status_code == 200

    body = r2.json()
    assert "output" in body
    assert "accepted" in body["output"]
    assert len(body["output"]["accepted"]) == 2
    assert "ingredients" in body["output"]["accepted"][0]
    assert body["output"]["accepted"][0]["ingredients"][0]["name"] == "Rice"
    assert body["version_snapshot"]["version"] == 2
    assert "diff" in body
    assert "explanations" in body
    assert isinstance(body["explanations"], list)

    # load-bearing checks
    assert "calories_changed" in body["diff"]
    assert body["diff"]["calories_changed"]["maintenance"]["from"] == 2600
    assert body["diff"]["calories_changed"]["maintenance"]["to"] == 2400

    # exact string from your explain_nutrition_diff() format
    assert "Calories: maintenance changed from 2600 to 2400." in body["explanations"]

def test_nutrition_regenerate_meal_swap_diff_is_deterministic(client):
    gen_req = {
        "targets": make_targets(2600),
        "diet": None,
        "allergies": [],
        "meals_needed": 2,
        "max_attempts": 1,
        "batch_size": 2,
    }

    r1 = client.post("/nutrition/generate", json=gen_req)
    assert r1.status_code == 200
    snap1 = r1.json()["version_snapshot"]

    # Keep calories the same so ONLY meal keys/names differ
    regen_req = {
        "prev_snapshot": snap1,
        "targets": make_targets(2600),
        "diet": None,
        "allergies": [],
        "meals_needed": 2,
        "max_attempts": 1,
        "batch_size": 2,
    }

    r2 = client.post("/nutrition/regenerate", json=regen_req)
    assert r2.status_code == 200
    body = r2.json()

    assert body["version_snapshot"]["version"] == 2

    # Diff should exist and should NOT contain calories_changed
    diff = body["diff"]
    assert isinstance(diff, dict)
    assert "calories_changed" not in diff

    # Meal swap should be deterministic: attempt 1 -> attempt 2
    # Assert via snapshot keys (strong + schema-agnostic)
    prev_keys = [m["key"] for m in snap1["accepted_meals"]]
    next_keys = [m["key"] for m in body["version_snapshot"]["accepted_meals"]]

    assert prev_keys == ["meal_1_(attempt_1)", "meal_2_(attempt_1)"]
    assert next_keys == ["meal_1_(attempt_2)", "meal_2_(attempt_2)"]

    # And explanations should mention the swap (if your explain includes meal changes)
    # If your explain doesn't include meal changes yet, delete these 2 asserts.
    joined = "\n".join(body["explanations"])
    assert "attempt 1" in joined
    assert "attempt 2" in joined

def test_macro_calc_stub_returns_implemented_false(client):
    r = client.post("/nutrition/macro-calc", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["implemented"] is False
    assert "scaffold" in body["message"].lower()

