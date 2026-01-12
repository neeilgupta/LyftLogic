# Phase 3 — Nutrition Engine

## Goals
- Deterministic calorie targets
- Zero-leak allergy handling
- Guaranteed vegan / vegetarian enforcement
- Safe LLM integration (LLM is never the authority)

## What Exists
### Calorie Engine
- Mifflin-St Jeor BMR
- Activity-based maintenance calories
- ±250 / ±500 / ±1000 kcal cut & bulk targets
- Deterministic macro breakdown

### Safety Enforcement (Fail-Closed)
- Every ingredient must declare:
  - contains[]
  - diet_tags[]
  - is_compound
- Missing or ambiguous data → rejected

### LLM Integration
- Bounded regeneration loop
- Validator is final authority
- Unsafe meals never reach output

## Why This Matters
- Prevents silent allergy leaks
- Prevents incorrect vegan/vegetarian meals
- Makes nutrition logic testable and extensible
