# Plan Diff v1 (Phase 1)

This document defines the human-readable diff format returned after applying a plan edit.
Goal: explain “what changed” and “why” without exposing internal rules-engine steps.

Diffs are plan-version to plan-version:
- before_plan (stored)
- after_plan (stored after patch + deterministic re-run)

---

## Principles

- Deterministic
- Readable
- Scoped
- Stable

---

## Canonical Diff Schema (v1)

{
  "reason": "string",
  "removed": [],
  "added": [],
  "modified": [],
  "notes": []
}

---

## Modified Item Schema

{
  "exercise": "string",
  "path": "weekly_split[i].main[j] | weekly_split[i].accessories[j]",
  "field": "name | sets | reps | rest_seconds | notes",
  "from": "any",
  "to": "any"
}

---

## Example — No barbells

{
  "reason": "No barbells constraint",
  "removed": ["Barbell Back Squat", "Romanian Deadlift"],
  "added": ["Hack Squat", "Seated Leg Curl"],
  "modified": [],
  "notes": ["Hard bans override preferences"]
}

---

## Out of scope

- Reordering
- Full JSON diff
- Rules-engine internals
