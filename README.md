# LyftLogic

LyftLogic is a deterministic training and nutrition planner built around one premise: AI should draft, code should decide.

Calories, macros, constraints, and edits are all handled in code. Plans are versioned, diffed, and explainable. Nothing changes silently.

---

## Demo

[Watch the LyftLogic demo](https://github.com/user-attachments/assets/666f5f96-7468-4654-8cee-8cf86c80feaa)

## Project Status (March 2026)

**Current state (v1 functional):**

### Training
- Deterministic plan generation
- Regeneration with versioned snapshots
- Index-stable diffs and explanations
- Restore previous versions
- Realistic lifting rules enforced in code

### Nutrition
- Deterministic meal generation
- Regeneration with versioned snapshots and diffs
- Hard allergen blocking (fail-closed)
- Diet constraints enforced
- Slot-based meals (breakfast / lunch / dinner / snack)
- Deterministic calorie repair (post-pass boosters)
- Slot-aware boosters (e.g. honey in oats, oil only in savory meals)
- Daily macro and calorie aims (guidance, not tracking)
- Debug data hidden behind toggle

### Macro Calculator
- Fully implemented (metric math)
- Used for guidance and target setting, not a hard constraint engine yet

### Accounts + Persistence
- Email + password registration and login
- Magic link (OTP) login
- Cookie-based sessions (httponly, samesite=lax)
- Email verification and password reset flows
- Account settings: change password, delete account (full data cascade)
- Plans and nutrition plans persisted to DB, scoped to owner
- My Plans dashboard: training and nutrition in one view
- Versioned plan history and restore

---

## Why LyftLogic Exists

Most fitness apps regenerate from scratch, trust AI output, and lose context on every edit. The plan you get on Monday looks nothing like Monday's plan by Wednesday, and you have no idea what changed or why.

LyftLogic is the opposite. Same inputs, same outputs. Changes are intentional, tracked, and reversible. If something differs between versions, you see exactly what and why.

The tradeoff: less novelty, more trust. That's the point.

---

## What LyftLogic Is Not

- A chat-until-it-looks-good app
- A black-box AI fitness tool
- A calorie tracker
- A system that resets state on regenerate

---

## Core Design Principles

**AI is never the source of truth.** LLMs generate drafts only. All outputs are validated and stabilized by deterministic rules engines before anything reaches the user.

**Constraints are enforced, not suggested.** If a rule exists, it rejects violations. There are no warnings.

**Plans evolve through versions.** Every change is deterministic, diffed, explained, and reversible. Nothing resets.

---

## Training System

Training plans are built around how experienced lifters actually program: low volume, long rest, compound-first, no filler.

**Rules enforced in code:**
- No cardio before lifting
- No finishers or accessory fluff
- Simple warmups (1 lighter set at ~50% before each lift)
- Low-to-moderate volume (default: 2 working sets per exercise)
- Long rest periods (4+ min compounds, 3+ min isolations)
- Rep ranges, not fixed reps
- Effort cues instead of RPE numbers
- Core lifts repeat across the week
- Primary compounds are never treated as accessories
- Session length caps exercise count
- Muscle focus prioritization: selected muscles surface their exercises first
- Glute-bias leg days get a fixed Hip Thrust-first structure
- Hamstring-focused days always include a squat-pattern movement

All plans support versioned snapshots, deterministic regeneration, diff rendering, and restore.

---

## Nutrition System

Nutrition gets the same treatment as training: hard rules, versioned history, no silent changes.

**Guaranteed behaviors:**
- Allergens are hard-blocked (fail-closed, not warned about)
- Diet constraints enforced
- No duplicate meals in a plan
- Deterministic calorie and macro math
- Supports maintenance, cut, and bulk (0.5 / 1 / 2 lb per week rates)
- Every regenerate produces a diff with plain-English explanations

### Calorie Repair

If a plan undershoots calories, a deterministic post-pass adds safe boosters. Boosters are diet-safe, allergy-safe, and slot-aware (no olive oil in oatmeal). No random retries, no silent adjustments.

---

## Macro Aims

LyftLogic doesn't do tracker UX. Instead, it shows:
- Daily calorie aim
- Protein aim: `0.8 g / lb bodyweight`
- Fat target: fixed % of calories
- Carbs: remainder (carb-forward by default)

---

## Versioning and Diffs

Both training and nutrition support versioned snapshots, index-stable diffs, and human-readable explanations. Every change is inspectable.

---

## Constraints Model

### Training
- Equipment bans
- Session length
- Split logic
- Compound caps
- Machine vs free-weight preference

### Nutrition
- Allergies (fail-closed)
- Diet type
- Calorie targets
- Meal count inference
- Context-preserving regeneration

---

## Architecture

1. **Draft generation (untrusted)** — LLM proposes structure only.
2. **Rules engines (authoritative)** — Enforce constraints, normalize outputs, stabilize plans.
3. **Version snapshot** — Immutable record of state.
4. **Diff and explanation** — Shown to the user in plain language.

No plan is shown unless it passes validation.

---

## Frontend

- Training and Nutrition are separate pages
- Debug data hidden behind toggles
- Diffs rendered explicitly
- UX favors clarity
- Auth-aware nav (email, settings, sign out)
- Account settings: view account info, change password, delete account

---

## Tech Stack

### Backend
- FastAPI (Python)
- SQLite (manual SQL, no ORM)
- Pydantic (strict schemas)
- Deterministic rules engines
- Versioned diff logic
- bcrypt for password hashing

### Frontend
- Nuxt 3 (Vue)
- TypeScript
- REST APIs
- Cookie-based auth (httponly, samesite=lax)
- Dark + purple UI

---

## Running Locally

### Backend
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Backend runs at:** http://127.0.0.1:8000

### Run Tests
```bash
pytest -q
```

### Frontend
```bash
cd apps/frontend
npm install
npm run dev
```

**Frontend runs at:** http://localhost:3000

---

## Scenarios Handled Correctly

- No dumbbells: zero leakage into plans
- No barbells: machine/cable substitutions applied
- 30-minute vs 75-minute sessions
- Beginner vs advanced lifters
- Rest days without filler
- Allergy-safe meal plans
- Calorie changes with explicit explanations

---

## Project Philosophy

LyftLogic is an engineering project. The goal isn't maximal personalization or a slick onboarding flow. It's a system where you can look at any output and understand exactly why it is the way it is.

Determinism is non-negotiable. AI drafts, code decides.
