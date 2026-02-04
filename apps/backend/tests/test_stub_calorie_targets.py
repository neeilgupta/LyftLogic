import re


def make_targets(maintenance: int):
    return {
        "maintenance": maintenance,
        "cut": {"0.5": maintenance - 250, "1": maintenance - 500, "2": maintenance - 1000},
        "bulk": {"0.5": maintenance + 250, "1": maintenance + 500, "2": maintenance + 1000},
    }


def _parse_calories(v) -> int:
    if isinstance(v, (int, float)):
        return int(round(float(v)))
    if isinstance(v, str):
        m = re.search(r"(\d+(?:\.\d+)?)", v)
        if m:
            return int(round(float(m.group(1))))
    return 0


def _meal_cals(meal: dict) -> int:
    if not isinstance(meal, dict):
        return 0
    if "calories" in meal:
        return _parse_calories(meal.get("calories"))
    macros = meal.get("macros")
    if isinstance(macros, dict) and "calories" in macros:
        return _parse_calories(macros.get("calories"))
    return 0


def _sum_plan_cals(meals: list[dict]) -> int:
    return sum(_meal_cals(m) for m in (meals or []) if isinstance(m, dict))


def _assert_within_15pct(total: int, target: int):
    lo = int(target * 0.85)
    hi = int(target * 1.15)
    assert lo <= total <= hi, f"total={total} not in [{lo},{hi}] for target={target}"


def test_stub_hits_maintenance_target_2790(client):
    req = {
        "targets": make_targets(2790),
        "target_calories": 2790,
        "diet": None,
        "allergies": [],
        "meals_needed": 0,  # infer from target
        "batch_size": 0,
        "max_attempts": 3,
    }
    r = client.post("/nutrition/generate", json=req)
    assert r.status_code == 200, r.text
    accepted = r.json()["output"]["accepted"]
    total = _sum_plan_cals(accepted)
    _assert_within_15pct(total, 2790)


def test_stub_hits_cut_target_1790(client):
    req = {
        "targets": make_targets(2790),
        "target_calories": 1790,
        "diet": None,
        "allergies": [],
        "meals_needed": 0,  # infer from target
        "batch_size": 0,
        "max_attempts": 3,
    }
    r = client.post("/nutrition/generate", json=req)
    assert r.status_code == 200, r.text
    accepted = r.json()["output"]["accepted"]
    total = _sum_plan_cals(accepted)
    _assert_within_15pct(total, 1790)


def test_stub_hits_high_target_3790(client):
    req = {
        "targets": make_targets(2790),
        "target_calories": 3790,
        "diet": None,
        "allergies": [],
        "meals_needed": 0,  # infer from target
        "batch_size": 0,
        "max_attempts": 5,
    }
    r = client.post("/nutrition/generate", json=req)
    assert r.status_code == 200, r.text
    accepted = r.json()["output"]["accepted"]
    total = _sum_plan_cals(accepted)
    _assert_within_15pct(total, 3790)


def test_meals_inference_boundaries(client):
    base = {
        "targets": make_targets(2600),
        "diet": None,
        "allergies": [],
        "meals_needed": 0,
        "batch_size": 0,
        "max_attempts": 3,
    }

    # 2299 -> 4 meals
    r1 = client.post("/nutrition/generate", json={**base, "target_calories": 2299})
    assert r1.status_code == 200, r1.text
    assert len(r1.json()["output"]["accepted"]) == 4

    # 2300 -> 5 meals
    r2 = client.post("/nutrition/generate", json={**base, "target_calories": 2300})
    assert r2.status_code == 200, r2.text
    assert len(r2.json()["output"]["accepted"]) == 5

    # 2801 -> 6 meals
    r3 = client.post("/nutrition/generate", json={**base, "target_calories": 2801})
    assert r3.status_code == 200, r3.text
    assert len(r3.json()["output"]["accepted"]) == 6
