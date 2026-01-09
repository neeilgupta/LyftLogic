import copy
import re
from models.plans import GeneratePlanRequest, GeneratePlanResponse
from routes.rules.engine import apply_rules_v1

BAD = re.compile(
    r"(shoulder press|overhead press|military press|arnold press|lateral raise|rear delt|reverse pec deck|face pull|upright row)",
    re.I,
)

def _all_names(output_json: dict) -> list[str]:
    names = []
    for d in output_json["weekly_split"]:
        if d.get("focus") == "Rest Day":
            continue
        for ex in (d.get("main", []) + d.get("accessories", [])):
            names.append(ex.get("name", "") or "")
    return names

def test_avoid_shoulders_no_leak(client):
    r = client.post("/plans/1/edit", json={"message": "avoid shoulders"})
    assert r.status_code == 200
    body = r.json()
    assert body["can_apply"] is True

    patch = body["proposed_patch"]
    r2 = client.post("/plans/1/apply", json=patch)
    assert r2.status_code == 200
    out = r2.json()["output"]

    names = _all_names(out)
    leaked = [n for n in names if BAD.search(n)]
    assert leaked == [], f"Shoulder leaks found: {leaked}"

def _mk_req():
    return GeneratePlanRequest(
        goal="hypertrophy",
        experience="intermediate",
        days_per_week=5,
        session_minutes=60,
        equipment="full_gym",
        soreness_notes="",
        constraints="AVOID: shoulders",
    )

def test_avoid_shoulders_filters_overhead_press():
    req = _mk_req()
    # generate a dummy plan by cloning a minimal valid structure:
    # easiest: call apply_rules_v1 on an empty-ish plan shape that matches your model schema.
    plan = GeneratePlanResponse(
        title="t",
        summary="",
        weekly_split=[],
        progression_notes=[],
        safety_notes=[],
    )


    out = apply_rules_v1(plan=copy.deepcopy(plan), req=req)

    bad = []
    for d in out.weekly_split:
        for ex in (d.main + d.accessories):
            n = (ex.name or "").lower()
            if ("shoulder press" in n) or ("lateral raise" in n) or ("rear delt" in n):
                bad.append(ex.name)

    assert not bad, f"Shoulder exercises leaked: {bad}"
def test_avoid_shoulders_no_leak(client):
    # 1) edit
    r = client.post("/plans/1/edit", json={"message": "avoid shoulders"})
    patch = r.json()["proposed_patch"]
    assert r.json()["can_apply"] is True

    # 2) apply
    r2 = client.post("/plans/1/apply", json=patch)
    out = r2.json()["output"]

    # 3) scan
    bad = ("shoulder press","overhead press","military press","arnold","lateral raise","rear delt","reverse pec deck","face pull","upright row")
    names = []
    for d in out["weekly_split"]:
        if d["focus"] == "Rest Day":
            continue
        for ex in (d["main"] + d["accessories"]):
            names.append((ex.get("name") or "").lower())
    assert not any(any(b in n for b in bad) for n in names)
