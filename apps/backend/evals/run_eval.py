"""
Eval harness: grid-test the rules engine across 240 input combinations.
Exits 1 if pass rate < 0.95.
"""
import sys
import os
import itertools

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.plans import GeneratePlanRequest, GeneratePlanResponse, DayPlan, ExerciseItem
from routes.rules.engine import apply_rules_v1
from evals.scoring import (
    session_time_within_budget,
    no_equipment_violations,
    no_duplicate_exercises,
    focus_muscles_prioritized,
    idempotent,
)

EVAL_GRID = {
    "days_per_week": [3, 4, 5, 6],
    "session_minutes": [30, 45, 60, 75],
    "equipment": ["full_gym", "dumbbells", "bodyweight"],
    "focus_muscles": [["chest"], ["back"], ["legs"], ["shoulders"], ["arms"]],
}

PASS_THRESHOLD = 0.95


def _base_plan() -> GeneratePlanResponse:
    """Minimal valid plan stub — engine pads/trims weekly_split as needed."""
    return GeneratePlanResponse(
        title="Eval Stub",
        summary="",
        weekly_split=[
            DayPlan(
                day="Day 1",
                focus="",
                warmup=[],
                main=[
                    ExerciseItem(name="Bench Press", sets=3, reps="8-12", rest_seconds=180)
                ],
                accessories=[],
            )
        ],
    )


def run_eval() -> tuple[int, int, list[str]]:
    total = 0
    passed = 0
    failures = []

    keys = list(EVAL_GRID.keys())
    combos = list(itertools.product(*EVAL_GRID.values()))

    for combo in combos:
        params = dict(zip(keys, combo))
        req = GeneratePlanRequest(
            days_per_week=params["days_per_week"],
            session_minutes=params["session_minutes"],
            equipment=params["equipment"],
            focus_muscles=params["focus_muscles"],
        )

        plan = apply_rules_v1(plan=_base_plan(), req=req)

        for day in plan.weekly_split:
            if not day.main and not day.accessories:
                continue  # REST day

            checks = {
                "session_time_within_budget": session_time_within_budget(day, req.session_minutes),
                "no_equipment_violations": no_equipment_violations(day, req.equipment),
                "no_duplicate_exercises": no_duplicate_exercises(day),
            }

            for check_name, result in checks.items():
                total += 1
                if result:
                    passed += 1
                else:
                    failures.append(
                        f"FAIL [{check_name}] days={req.days_per_week} mins={req.session_minutes} "
                        f"equip={req.equipment} focus={req.focus_muscles} day={day.day}"
                    )

        # Plan-level checks (counted once per combo)
        plan_checks = {
            "focus_muscles_prioritized": focus_muscles_prioritized(plan, req.focus_muscles),
            "idempotent": idempotent(_base_plan(), req),
        }

        for check_name, result in plan_checks.items():
            total += 1
            if result:
                passed += 1
            else:
                failures.append(
                    f"FAIL [{check_name}] days={req.days_per_week} mins={req.session_minutes} "
                    f"equip={req.equipment} focus={req.focus_muscles}"
                )

    return passed, total, failures


def main():
    passed, total, failures = run_eval()
    rate = passed / total if total > 0 else 0.0

    print(f"\nEval results: {passed}/{total} checks passed ({rate:.1%})")

    if failures:
        print(f"\nFailures ({len(failures)}):")
        for f in failures:
            print(f"  {f}")

    if rate < PASS_THRESHOLD:
        print(f"\nFAIL: pass rate {rate:.1%} < threshold {PASS_THRESHOLD:.0%}")
        sys.exit(1)
    else:
        print(f"\nPASS: pass rate {rate:.1%} >= threshold {PASS_THRESHOLD:.0%}")


if __name__ == "__main__":
    main()
