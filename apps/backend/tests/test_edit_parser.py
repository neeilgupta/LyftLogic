from models.plans import EditPlanRequest
from routes.plans import edit_saved_plan

class DummyReq:
    def __init__(self, message: str):
        self.message = message


def call(msg: str):
    # plan_id doesn't matter for parser logic
    return edit_saved_plan(plan_id=1, body=DummyReq(msg))


def test_no_barbells():
    res = call("no barbells")
    assert res.can_apply is True
    assert "no_barbells" in res.proposed_patch.constraints_add


def test_no_dumbbells():
    res = call("no dumbbells")
    assert res.can_apply is True
    assert "no_dumbbells" in res.proposed_patch.constraints_add


def test_prefer_machines():
    res = call("prefer machines")
    assert res.can_apply is True
    assert "prefer_machines" in res.proposed_patch.preferences_add


def test_focus_arms():
    res = call("focus arms")
    assert res.can_apply is True
    assert res.proposed_patch.emphasis == "arms"


def test_avoid_lower_back():
    res = call("avoid lower back")
    assert res.can_apply is True
    assert "lower_back" in res.proposed_patch.avoid


def test_unknown_message():
    res = call("make it spicy")
    assert res.can_apply is False
    assert len(res.errors) > 0
