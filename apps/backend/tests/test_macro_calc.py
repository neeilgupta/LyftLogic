import pytest

from services.nutrition.macros import calculate_macro_calc_v4_metric


def test_macro_calc_v4_metric_mifflin_tdee_and_rounding():
    """
    Male, 25y, 180cm, 80kg
    BMR (Mifflin metric) = 10*80 + 6.25*180 - 5*25 + 5 = 1805
    Activity (moderate=1.55) => TDEE = 1805*1.55 = 2797.75
    Maintenance rounded to nearest 10 => 2800
    """
    out = calculate_macro_calc_v4_metric(
        sex="male",
        age=25,
        height_cm=180,
        weight_kg=80,
        activity_level="moderate",
    )

    assert out["bmr"] == 1805
    assert out["activity_multiplier"] == 1.55

    assert out["tdee"] == pytest.approx(2797.75, rel=0, abs=1e-6)
    assert out["maintenance"] == 2800

    t = out["targets"]
    assert t["maintenance"] == 2800
    assert t["cut"]["0.5"] == 2550
    assert t["cut"]["1"] == 2300
    assert t["cut"]["2"] == 1800
    assert t["bulk"]["0.5"] == 3050
    assert t["bulk"]["1"] == 3300
    assert t["bulk"]["2"] == 3800

    # Explanation should be stable + human-readable
    expl = out["explanation"]
    assert "Mifflin" in expl
    assert "Activity multiplier" in expl
    assert "Maintenance (rounded to nearest 10)" in expl
    assert "Rate deltas" in expl


@pytest.mark.parametrize(
    "lvl, expected",
    [
        ("sedentary", 1.2),
        ("light", 1.375),
        ("moderate", 1.55),
        ("very", 1.725),
        ("athlete", 1.9),
    ],
)
def test_activity_multiplier_mapping_is_exact(lvl, expected):
    out = calculate_macro_calc_v4_metric(
        sex="male",
        age=25,
        height_cm=180,
        weight_kg=80,
        activity_level=lvl,
    )
    assert out["activity_multiplier"] == expected

def test_macro_calc_route_selected_mapping(client):
    req = {
        "sex": "male",
        "age": 25,
        "height_cm": 180,
        "weight_kg": 80,
        "activity_level": "moderate",
        "goal": "cut",
        "rate": "1",
    }
    r = client.post("/nutrition/macro-calc", json=req)
    assert r.status_code == 200
    body = r.json()

    sel = body["macros"]["selected"]
    assert sel["goal"] == "cut"
    assert sel["rate"] == "1"
    assert sel["calories"] == body["macros"]["targets"]["cut"]["1"]

    # Maintenance ignores rate deterministically
    req2 = {**req, "goal": "maintenance", "rate": "2"}
    r2 = client.post("/nutrition/macro-calc", json=req2)
    assert r2.status_code == 200
    sel2 = r2.json()["macros"]["selected"]
    assert sel2["goal"] == "maintenance"
    assert sel2["rate"] is None
    assert sel2["calories"] == r2.json()["macros"]["targets"]["maintenance"]



def test_activity_aliases_are_supported_but_canonicalized():
    # alias: active -> very
    out = calculate_macro_calc_v4_metric(
        sex="male",
        age=25,
        height_cm=180,
        weight_kg=80,
        activity_level="active",
    )
    assert out["activity_multiplier"] == 1.725

    # alias: very_active -> athlete
    out2 = calculate_macro_calc_v4_metric(
        sex="male",
        age=25,
        height_cm=180,
        weight_kg=80,
        activity_level="very_active",
    )
    assert out2["activity_multiplier"] == 1.9


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        calculate_macro_calc_v4_metric(
            sex="male",
            age=0,
            height_cm=180,
            weight_kg=80,
            activity_level="moderate",
        )
    with pytest.raises(ValueError):
        calculate_macro_calc_v4_metric(
            sex="male",
            age=25,
            height_cm=-1,
            weight_kg=80,
            activity_level="moderate",
        )
    with pytest.raises(ValueError):
        calculate_macro_calc_v4_metric(
            sex="male",
            age=25,
            height_cm=180,
            weight_kg=0,
            activity_level="moderate",
        )
    with pytest.raises(ValueError):
        calculate_macro_calc_v4_metric(
            sex="male",
            age=25,
            height_cm=180,
            weight_kg=80,
            activity_level="nonsense",
        )


def test_macro_calc_route_validation_and_shape(client):
    # Missing fields -> route should 422 (fail-closed)
    r = client.post("/nutrition/macro-calc", json={})
    assert r.status_code == 422

    # Bad activity -> 422
    bad = {
        "sex": "male",
        "age": 25,
        "height_cm": 180,
        "weight_kg": 80,
        "activity_level": "nope",
    }
    r2 = client.post("/nutrition/macro-calc", json=bad)
    assert r2.status_code == 422

    # Valid -> deterministic shape + implemented true
    good = {
        "sex": "male",
        "age": 25,
        "height_cm": 180,
        "weight_kg": 80,
        "activity_level": "moderate",
    }
    r3 = client.post("/nutrition/macro-calc", json=good)
    assert r3.status_code == 200
    body = r3.json()

    assert body["implemented"] is True
    assert body["message"] == "ok"
    assert "macros" in body
    assert set(body["macros"]["targets"].keys()) == {"maintenance", "cut", "bulk"}
