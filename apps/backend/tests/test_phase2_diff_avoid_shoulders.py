import copy
import json
import re
from types import SimpleNamespace

from models.plans import GeneratePlanRequest, GeneratePlanResponse
from routes.rules.engine import apply_rules_v1
from services.plan_diff import compute_plan_diff


# Keep this list small + high-signal. We only want obvious shoulder-dominant leaks.
BAD = re.compile(
    r"(shoulder press|overhead press|military press|arnold press|lateral raise|rear delt|reverse pec deck|face pull|upright row)",
    re.I,
)


def _all_names(output_json: dict) -> list[str]:
    names: list[str] = []
    for day in output_json.get("weekly_split", []):
        if day.get("focus") == "Rest Day":
            continue
        for ex in (day.get("main", []) + day.get("accessories", [])):
            names.append(ex.get("name", "") or "")
    return names


def test_apply_avoid_shoulders_produces_diff_and_no_leak(client):
    """Phase 2 lock: applying 'avoid shoulders' must (a) return a diff and (b) produce zero shoulder leakage."""

    # 1) edit
    r = client.post("/plans/1/edit", json={"message": "avoid shoulders"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["can_apply"] is True

    patch = body["proposed_patch"]

    # 2) apply
    r2 = client.post("/plans/1/apply", json=patch)
    assert r2.status_code == 200, r2.text
    applied = r2.json()

    # 3) diff exists + shows a real change
        # 0) load base plan so we can tell whether a change is expected
    r0 = client.get("/plans/1")
    assert r0.status_code == 200, r0.text
    base = r0.json()
    base_names = _all_names(base["output"])
    base_has_shoulders = any(BAD.search(n) for n in base_names)

    # 3) diff exists (contract)
    assert "diff" in applied and applied["diff"] is not None
    diff = applied["diff"]
    if base_has_shoulders:
        # If a change happened, every emitted diff entry should include the reason hint.
        for k in ("replaced_exercises", "removed_exercises", "added_exercises"):
            for entry in diff.get(k, []):
                assert entry.get("reason") == "avoid_shoulders", f"Missing/incorrect reason on {k}: {entry}"

    # If the base plan had shoulder moves, we MUST see a change.
    # If it didn't, diff is allowed to be empty.
    if base_has_shoulders:
        assert any(
            len(diff.get(k, [])) > 0
            for k in ("replaced_exercises", "removed_exercises", "added_exercises")
        ), f"Expected non-empty diff (base had shoulders), got: {diff}"


    # 4) no shoulder leaks in final plan
    out = applied["output"]
    names = _all_names(out)
    leaked = [n for n in names if BAD.search(n)]
    assert leaked == [], f"Shoulder leaks found: {leaked}"


def test_diff_is_deterministic_unit_level(client):
    """Determinism check without needing a fresh DB plan.

    We re-run the deterministic engine twice from the same base output and compare:
      - output JSON
      - computed diff JSON
    """

    # Pull an existing stored plan (ships with repo DB) and use its output as the base.
    r = client.get("/plans/1")
    assert r.status_code == 200, r.text
    base = r.json()
    base_output = base["output"]

    # Build a request-like object the same way /apply does.
    base_input = base["input"]
    req_fields = {k: base_input.get(k) for k in GeneratePlanRequest.model_fields.keys()}
    req_obj = SimpleNamespace(**req_fields, avoid=["shoulders"])

    # Run twice from the exact same base.
    plan_obj_1 = GeneratePlanResponse(**copy.deepcopy(base_output))
    plan_obj_2 = GeneratePlanResponse(**copy.deepcopy(base_output))

    out1 = apply_rules_v1(plan=plan_obj_1, req=req_obj).model_dump()
    out2 = apply_rules_v1(plan=plan_obj_2, req=req_obj).model_dump()

    diff1 = compute_plan_diff(base_output, out1, reason="avoid_shoulders")
    diff2 = compute_plan_diff(base_output, out2, reason="avoid_shoulders")


    assert json.dumps(out1, sort_keys=True) == json.dumps(out2, sort_keys=True)
    assert json.dumps(diff1, sort_keys=True) == json.dumps(diff2, sort_keys=True)
