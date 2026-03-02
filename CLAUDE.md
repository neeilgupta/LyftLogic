# LyftLogic — Claude Project Memory

## One-Liner
Deterministic, versioned fitness planning engine. FastAPI + SQLite. Correctness > speed. Not a chatbot.

---

## Project Structure
```
LyftLogic/
├── main.py                        # Entry point — has known double-import bug
├── apps/
│   ├── frontend/                  # Nuxt 3 + Vue
│   │   ├── app/pages/             # index, generate, plans/[id], nutrition, roadmap
│   │   ├── app/components/        # NutritionDiff, LLLoadingPanel, AppTopNav
│   │   └── composables/           # usePlans.ts, useAuth.ts
│   └── data/gymgpt.db             # SQLite DB (auto-created)
├── routes/
│   ├── auth.py                    # OTP flow, sessions, cookies
│   ├── plans.py                   # 7 endpoints: generate, list, get, edit, apply, versions, restore
│   ├── nutrition.py               # generate, regenerate, macro-calc
│   ├── logs.py                    # EXISTS BUT NOT MOUNTED in main.py
│   ├── feedback.py                # EMPTY FILE
│   └── rules/
│       ├── engine.py              # apply_rules_v1() — 1399 lines, core rules engine
│       └── exercise_catalog.py   # 114 exercises with kind/region/tags
├── models/
│   ├── plans.py                   # GeneratePlanRequest, ExerciseItem, DayPlan, etc.
│   └── nutrition.py               # NutritionTargets, MacroCalcRequest/Response, etc.
└── services/
    ├── db.py                      # init_db(), all migrations, all DB helpers
    ├── nutrition/
    │   ├── macros.py              # BMR + TDEE (Mifflin-St Jeor), calorie targets
    │   ├── stub_meals.py          # Slot assignment, scaling, macro_close_v1
    │   ├── meal_library.py        # Static meal templates (~60KB, hand-curated)
    │   ├── ingredients_pantry.py  # ~120 ingredients, per-100g macro lookup
    │   ├── generate.py            # Accept/reject loop, deduplication
    │   ├── boosters.py            # Post-gen calorie fill (rice/oats/olive oil)
    │   ├── allergens.py           # Allergen alias expansion, diet enforcement
    │   ├── contracts.py           # TypedDicts: Ingredient, Meal, NutritionVersionV1
    │   ├── versioning.py          # Snapshot builder, diff engine, human-readable diffs
    │   └── regenerate.py          # Thin wrapper: regenerate -> snapshot -> diff
    ├── plan_diff.py               # compute_plan_diff() — slot-aligned comparison
    ├── llm.py                     # ORPHANED — explain_workout(), coach_reply() not wired
    ├── planner.py                 # DEAD CODE — superseded by LLM+rules engine
    └── nlp.py                     # DEAD CODE — paired with legacy planner.py
```

---

## DB Schema
| Table | Key Columns | Notes |
|---|---|---|
| `logs` | id, name, reps, weight_kg, rir, focus, timestamp | Workout log entries |
| `plans` | id, created_at, title, input_json, output_json, owner_id | owner_id NULL for legacy |
| `plan_versions` | id, plan_id FK, version, input/output/diff_json | UNIQUE(plan_id, version), CASCADE |
| `users` | id, email UNIQUE, created_at | Email-only identity |
| `sessions` | token PK, user_id FK, created_at, expires_at | expires_at NOT NULL enforced |
| `login_codes` | id, email, code_hash, expires_at, used | SHA-256 OTP, single-use |

Migrations run every startup (all idempotent): diff_json column, owner_id column, session expiry backfill, index hardening.

---

## How the Two Engines Work

### Training Plan Engine
```
POST /plans/generate
  -> OpenAI gpt-4o-mini (structured JSON, strict schema)   <- just a scaffold
  -> apply_rules_v1(plan, req)                              <- OVERWRITES exercises entirely
      -> _select_day_templates()    (days 1-6: FB/Upper-Lower/PPL)
      -> _apply_template()          (priority-ordered exercise slots)
      -> _enforce_equipment()       (ban/swap dumbbells, barbells)
      -> _enforce_prefer_cables()   (cable swap map)
      -> _enforce_avoid_shoulders() (blocklist enforcement)
      -> _normalize_sets/reps/rest  (hard clamps: 1-3 sets, 6-8/8-12 only, 240s compounds)
      -> _enforce_session_minutes() (time model: drop/add accessories)
  -> add_plan() -> DB

POST /plans/{id}/apply  (EDITS — NO LLM)
  -> regex parse intent -> PlanEditPatch
  -> merge patch into input_state
  -> re-run apply_rules_v1() on existing output
  -> compute_plan_diff() -> new version
```

LLM generates: title, summary, focus names, warmup bullets, notes
Rules engine generates: ALL exercises (100% deterministic)

### Nutrition Engine
```
POST /nutrition/generate
  -> macros.py: Mifflin-St Jeor BMR x activity -> TDEE -> targets
  -> route: _infer_target_calories(), _infer_meals_needed()
  -> stub_meals.py: slot budgets -> deterministic pick -> scale -> macro_close_v1()
  -> generate.py: accept/reject loop (allergen + diet + calorie cap + dedup)
  -> boosters.py: fill gap with rice/oats/olive oil if under target
  -> versioning.py: build snapshot
```

No LLM involved — llm_generate param exists but always receives _stub_llm_generate (static MEAL_LIBRARY).
Macro math source of truth: ingredients_pantry.py (gram weights x per-100g values).
Calorie closing is carb-only — _macro_close_v1 only adjusts carb-bearing ingredients.

---

## Known Bugs / Tech Debt

| Issue | File | Severity |
|---|---|---|
| plans_router + auth_router imported twice | main.py lines 3-4 and 34-36 | Medium |
| logs_router never registered | main.py | High |
| feedback.py is empty | routes/feedback.py | Low |
| PRAGMA table_info check on every DB call | services/db.py 307/342/374 | Low |
| add_plan() commits plan before version insert | services/db.py 320-327 | Medium |
| services/llm.py orphaned | services/llm.py | Low |
| services/planner.py dead code | services/planner.py | Low |
| services/nlp.py dead code | services/nlp.py | Low |
| No rate limiting on /auth/request-code | routes/auth.py | HIGH |
| secure=False on cookies | routes/auth.py | HIGH (prod) |
| Nutrition endpoints not auth-scoped | routes/nutrition.py | Medium |

---

## Non-Negotiables (Never Violate)
1. Determinism — same input -> same output, always
2. Slot-first meal generation — generate by slots, infer count from calories, meals_needed is override
3. AI output is untrusted — parse + validate; reject if schema invalid
4. Snapshots are immutable — never overwrite, always version
5. Owner scoping on every query — WHERE owner_id = current_user.id; NULL guard for legacy
6. Cookie sessions, not JWT — httponly, samesite=lax, server-side store
7. No randomness in training engine — rule trees only
8. Manual SQL — no ORM, explicit queries
9. Guardrails before features — incorrect output is worse than no output

---

## Priority Order (Next Tasks)
1. Fix double imports + mount logs_router in main.py (5 min quick win)
2. Rate limiting on /auth/request-code (per-IP + per-email)
3. secure=True on cookies (env-gated: if os.getenv("ENV") == "production")
4. Auth-scope nutrition endpoints (add get_current_user dependency)
5. Fix add_plan() transaction atomicity (wrap plan + version insert together)
6. Phase 5: plan lifecycle (GET/POST /plans, active_plan_id on users table)
7. Training progression state table (exercise_id, last_weight, last_reps, last_progression)
8. reconcile_macros() — strict enforcement that protein*4 + carbs*4 + fats*9 == calories
9. Dead code cleanup (planner.py, nlp.py, llm.py)

---

## Coding Style
- Explicit over implicit — guard clauses early
- Validation before persistence
- Small, clear functions
- No hidden state, no silent mutation
- Controlled state transitions
- Reliability > Flashiness — Infrastructure > UI — Correctness > Speed

---

## How to Work With Neeil
- Plan in Claude chat -> Execute in Claude Code
- When suggesting implementation: name the exact file + function to change
- When reviewing: check owner scoping, determinism, validation layer first
- Never suggest JWT, ORMs, or raw LLM output without a validation layer
- Phase tasks — don't suggest doing everything at once
- Incorrect output is worse than no output — always validate before returning