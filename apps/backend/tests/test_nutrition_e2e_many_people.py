import hashlib
import json
import re
import pytest


# ---------- helpers ----------

def make_targets(maintenance: int):
    # aligns with your UI display: cut/bulk tiers around maintenance
    return {
        "maintenance": maintenance,
        "cut": {"0.5": maintenance - 250, "1": maintenance - 500, "2": maintenance - 1000},
        "bulk": {"0.5": maintenance + 250, "1": maintenance + 500, "2": maintenance + 1000},
    }


def _parse_num(x) -> float:
    if x is None:
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x)
    m = re.search(r"(-?\d+(?:\.\d+)?)", s)
    return float(m.group(1)) if m else 0.0


def meal_calories(meal: dict) -> int:
    if not isinstance(meal, dict):
        return 0
    if "calories" in meal:
        return int(round(_parse_num(meal["calories"])))
    macros = meal.get("macros") or {}
    return int(round(_parse_num(macros.get("calories", 0))))


def sum_plan_calories(meals: list[dict]) -> int:
    return sum(meal_calories(m) for m in (meals or []) if isinstance(m, dict))


def within_pct(total: int, target: int, pct: float = 0.15) -> bool:
    lo = int(target * (1.0 - pct))
    hi = int(target * (1.0 + pct))
    return lo <= total <= hi


def assert_within_pct(total: int, target: int, pct: float = 0.15):
    lo = int(target * (1.0 - pct))
    hi = int(target * (1.0 + pct))
    assert lo <= total <= hi, f"total={total} not in [{lo},{hi}] for target={target}"


def _stable_digest(obj) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def post_generate(client, payload: dict):
    r = client.post("/nutrition/generate", json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    accepted = j["output"]["accepted"]
    return j, accepted


def post_regen(client, payload: dict):
    r = client.post("/nutrition/regenerate", json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    accepted = j["output"]["accepted"]
    return j, accepted


# ---------- “people” (macro-calc-like scenarios) ----------

PEOPLE = [
    # name, maintenance (approx), goal, tier, explicit_target_override
    ("lean_male_20_5_9_150_moderate", 2500, "maintenance", None, None),
    ("male_25_5_11_175_moderate",     2790, "bulk",        "2", 3790),
    ("male_25_6_5_170_very",          3230, "bulk",        "1", 3730),
    ("female_22_5_4_125_light",       1900, "cut",         "1", 1400),
    ("female_30_5_6_145_moderate",    2100, "maintenance", None, None),
    ("male_35_6_2_220_sedentary",     2600, "cut",         "2", 1600),
    ("male_19_6_0_180_very",          3100, "bulk",        "2", 4100),
    ("female_27_5_7_160_very",        2600, "bulk",        "0.5", 2850),
    ("small_cut_edge_1790",           2790, "cut",         None, 1790),
    ("high_bulk_edge_3790",           2790, "bulk",        None, 3790),
]

# We also test some “reasonable” random-ish-but-deterministic targets
TARGET_SWEEP = [
    1200, 1400, 1600, 1790, 1900, 2100, 2299, 2300, 2400, 2600, 2790, 2801, 3000, 3230, 3500, 3730, 3790, 4100
]


# ---------- core tests ----------

@pytest.mark.parametrize("name,maint,goal,tier,explicit_target", PEOPLE)
def test_generate_many_people_hits_calories(client, name, maint, goal, tier, explicit_target):
    targets = make_targets(maint)

    # choose target calories:
    if explicit_target is not None:
        target = explicit_target
    else:
        # if no explicit, pick maintenance or tier-based from targets
        if goal == "maintenance":
            target = targets["maintenance"]
        elif goal == "cut":
            target = int(targets["cut"].get(tier or "1"))
        else:
            target = int(targets["bulk"].get(tier or "1"))

    payload = {
        "targets": targets,
        "target_calories": target,
        "diet": None,
        "allergies": [],
        "meals_needed": 0,  # infer
        "batch_size": 0,
        "max_attempts": 6,
    }

    _, accepted = post_generate(client, payload)
    total = sum_plan_calories(accepted)
    assert_within_pct(total, target, pct=0.15)


@pytest.mark.parametrize("target", TARGET_SWEEP)
def test_generate_target_sweep_hits_calories(client, target):
    # maintenance target table isn't important for stub; but routes expect it
    targets = make_targets(2600)
    payload = {
        "targets": targets,
        "target_calories": target,
        "diet": None,
        "allergies": [],
        "meals_needed": 0,   # infer
        "batch_size": 0,
        "max_attempts": 8,
    }

    _, accepted = post_generate(client, payload)
    total = sum_plan_calories(accepted)

    # We allow looser at extreme low targets (1200/1400) but still must be reasonable.
    pct = 0.20 if target <= 1400 else 0.15
    assert_within_pct(total, target, pct=pct)


def test_inference_boundaries_meals_count(client):
    targets = make_targets(2600)
    base = {"targets": targets, "diet": None, "allergies": [], "meals_needed": 0, "batch_size": 0, "max_attempts": 4}

    _, a1 = post_generate(client, {**base, "target_calories": 2299})
    assert len(a1) == 4

    _, a2 = post_generate(client, {**base, "target_calories": 2300})
    assert len(a2) == 5

    _, a3 = post_generate(client, {**base, "target_calories": 2801})
    assert len(a3) == 6


@pytest.mark.parametrize("meals_needed", [2, 3, 4, 5, 6])
def test_explicit_meals_override_respected(client, meals_needed):
    targets = make_targets(2790)
    payload = {
        "targets": targets,
        "target_calories": 2790,
        "diet": None,
        "allergies": [],
        "meals_needed": meals_needed,  # override
        "batch_size": 0,
        "max_attempts": 6,
    }
    _, accepted = post_generate(client, payload)
    assert len(accepted) == meals_needed
    total = sum_plan_calories(accepted)
    assert_within_pct(total, 2790, pct=0.15)


def test_determinism_same_inputs_same_output(client):
    targets = make_targets(2790)
    payload = {
        "targets": targets,
        "target_calories": 3290,
        "diet": None,
        "allergies": [],
        "meals_needed": 0,
        "batch_size": 0,
        "max_attempts": 6,
    }

    j1, a1 = post_generate(client, payload)
    j2, a2 = post_generate(client, payload)

    # Use a digest of accepted meals only (order + grams must match).
    d1 = _stable_digest(a1)
    d2 = _stable_digest(a2)

    assert d1 == d2, "stub generation must be deterministic for identical inputs"


def test_regenerate_is_deterministic_by_attempt_seed(client):
    targets = make_targets(2790)

    gen_payload = {
        "targets": targets,
        "target_calories": 2790,
        "diet": None,
        "allergies": [],
        "meals_needed": 0,   # sentinel OK for /generate
        "batch_size": 0,     # sentinel OK for /generate
        "max_attempts": 6,
    }

    j1, _ = post_generate(client, gen_payload)

    # Your API returns it here
    prev_snapshot = j1.get("version_snapshot")
    assert prev_snapshot is not None, f"generate response missing version_snapshot keys: {list(j1.keys())}"

    # /regenerate has stricter validation: meals_needed and batch_size must be >= 1
    regen_payload = {
        "prev_snapshot": prev_snapshot,
        "targets": targets,
        "target_calories": 2790,
        "diet": None,
        "allergies": [],
        "meals_needed": 5,
        "batch_size": 5,
        "max_attempts": 6,
    }

    _, r1 = post_regen(client, regen_payload)
    _, r2 = post_regen(client, regen_payload)

    assert _stable_digest(r1) == _stable_digest(r2), "regen should be deterministic for identical inputs"

# ---------- diet/allergy fail-closed tests ----------

@pytest.mark.parametrize("diet", ["vegan", "vegetarian", "pescatarian"])
def test_diet_enforced_fail_closed(client, diet):
    targets = make_targets(2600)
    payload = {
        "targets": targets,
        "target_calories": 2600,
        "diet": diet,
        "allergies": [],
        "meals_needed": 0,
        "batch_size": 0,
        "max_attempts": 10,
    }
    _, accepted = post_generate(client, payload)

    # Every ingredient must have a matching diet tag intersection.
    required = {diet}
    if diet == "vegetarian":
        required = {"vegetarian", "vegan"}
    if diet == "pescatarian":
        required = {"pescatarian", "vegetarian", "vegan"}

    for meal in accepted:
        for ing in meal.get("ingredients", []):
            tags = {str(t).lower() for t in (ing.get("diet_tags") or [])}
            assert tags & required, f"diet={diet} violated by ingredient {ing.get('name')} tags={tags}"


@pytest.mark.parametrize("allergen", ["almonds", "peanuts", "shellfish", "milk", "egg", "soy", "wheat"])
def test_allergy_block_contains_tags_fail_closed(client, allergen):
    targets = make_targets(2600)
    payload = {
        "targets": targets,
        "target_calories": 2600,
        "diet": None,
        "allergies": [allergen],
        "meals_needed": 0,
        "batch_size": 0,
        "max_attempts": 12,
    }
    _, accepted = post_generate(client, payload)

    blocked = {allergen.lower()}
    # Your allergen tool may expand tokens; but at minimum ingredient contains must not intersect.
    for meal in accepted:
        for ing in meal.get("ingredients", []):
            contains = {str(t).lower() for t in (ing.get("contains") or [])}
            assert not (contains & blocked), f"allergen={allergen} violated by {ing.get('name')} contains={contains}"


def test_allergy_hard_case_nuts_blocks_trailmix(client):
    targets = make_targets(2600)
    payload = {
        "targets": targets,
        "target_calories": 2600,
        "diet": None,
        "allergies": ["nuts"],
        "meals_needed": 0,
        "batch_size": 0,
        "max_attempts": 12,
    }
    _, accepted = post_generate(client, payload)

    # Should not include common nut-containing snacks if contains tags are correct
    for meal in accepted:
        for ing in meal.get("ingredients", []):
            contains = {str(t).lower() for t in (ing.get("contains") or [])}
            assert "tree_nut" not in contains and "peanut" not in contains, \
                f"nuts allergy violated by {ing.get('name')} contains={contains}"
