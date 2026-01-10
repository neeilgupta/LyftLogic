import json


def _canonical(x):
    return json.dumps(x, sort_keys=True)


def test_restore_creates_new_version_and_restores_exact_snapshot(client):
    # Get current latest version
    r0 = client.get("/plans/1")
    assert r0.status_code == 200, r0.text
    base = r0.json()
    start_version = base["version"]

    # Make a change to ensure we have something to restore from
    r1 = client.post("/plans/1/edit", json={"message": "prefer cables"})
    assert r1.status_code == 200, r1.text
    assert r1.json()["can_apply"] is True
    patch = r1.json()["proposed_patch"]

    r2 = client.post("/plans/1/apply", json=patch)
    assert r2.status_code == 200, r2.text
    applied = r2.json()
    after_apply_version = applied["version"]
    assert after_apply_version == start_version + 1

    # Target = version before apply
    target_version = start_version

    # Fetch the snapshot we plan to restore
    r3 = client.get("/plans/1/versions")
    assert r3.status_code == 200, r3.text
    versions = r3.json()["items"]
    target = next(v for v in versions if v["version"] == target_version)
    target_output = target["output"]

    # Restore it
    r4 = client.post("/plans/1/restore", json={"version": target_version})
    assert r4.status_code == 200, r4.text
    restored = r4.json()

    assert restored["version"] == after_apply_version + 1
    assert restored["diff"] == {"restored_from": target_version}

    # Latest plan output must match target EXACTLY
    r5 = client.get("/plans/1")
    assert r5.status_code == 200, r5.text
    latest = r5.json()

    assert _canonical(latest["output"]) == _canonical(target_output)
