# LyftLogic

LyftLogic is a **deterministic training and nutrition planning system** built for people who care about *consistency, realism, and trust*.

Instead of treating AI output as truth, LyftLogic treats AI as an **untrusted draft generator**.
All important logic — constraints, calories, macros, structure, and edits — is enforced **deterministically in code**.

The result: plans that are **stable, explainable, versioned, and human-sane** — not vibes-based.

---

## Demo

[Watch the LyftLogic demo](https://github.com/user-attachments/assets/666f5f96-7468-4654-8cee-8cf86c80feaa)

## Project Status (March 2026)

**Current state (v1 functional):**

### Training
- Deterministic plan generation
- Regeneration with versioned snapshots
- Index-stable diffs + explanations
- Restore previous versions
- Realistic lifting rules enforced in code

### Nutrition
- Deterministic meal generation
- Regeneration with versioned snapshots + diffs
- Hard allergen blocking (fail-closed)
- Diet constraints enforced
- Slot-based meals (breakfast / lunch / dinner / snack)
- Deterministic calorie repair (post-pass boosters)
- Slot-aware boosters (e.g. honey in oats, oil only in savory meals)
- Daily macro & calorie aims (guidance, not tracking)
- Debug data hidden behind toggle

### Macro Calculator
- Fully implemented (metric math)
- Used for guidance + target setting (not yet a hard constraint engine)

### Accounts + Persistence
- Email + password registration and login
- Magic link (OTP) login
- Cookie-based sessions (httponly, samesite=lax)
- Email verification + password reset flows
- Account settings — change password, delete account (full data cascade)
- Plans and nutrition plans persisted to DB, scoped to owner
- My Plans dashboard — training + nutrition in one view
- Versioned plan history + restore

---

## Why LyftLogic Exists

Most fitness apps:
- Trust AI output blindly
- Regenerate from scratch
- Lose context on every edit
- Hide logic behind "smart recommendations"

LyftLogic does the opposite.

**Design priorities:**
1. **Trust through verifiability** — Every rule is explicit, enforced, and auditable.
2. **Determinism over novelty** — Same inputs produce same outputs. Changes are intentional and tracked.
3. **Explainability over magic** — If something changes, you see why.

This trades novelty for confidence — by design.

---

## What LyftLogic Is Not

- A chat-until-it-looks-good app
- A black-box AI fitness tool
- A calorie tracker
- A system that resets state on regenerate

---

## Core Design Principles

### 1) AI is never the source of truth
LLMs generate drafts only.
All outputs are validated, corrected, and stabilized by deterministic rules engines.

### 2) Constraints are enforced, not suggested
If a rule exists, it is enforced in code.
Violations are rejected — not "warned about".

### 3) Plans evolve through versions
Plans never reset.
They change, and every change is:
- deterministic
- diffed
- explained
- reversible

---

## Training System (Realism-First)

Training plans resemble how experienced lifters actually program.

**Hard rules enforced in code:**
- No cardio before lifting
- No finishers or fluff
- Simple warmups (1 lighter set ~50% before each lift)
- Low-to-moderate volume (default: 2 working sets per exercise)
- Long rest periods (4+ min compounds, 3+ min isolations)
- Rep ranges, not fixed reps
- Effort cues instead of RPE
- Core lifts repeat across the week
- Primary compounds are never accessories
- Session length strictly limits exercise count
- Muscle focus prioritization — selected muscles surface their exercises first in the plan
- Glute-bias leg days get a fixed, Hip Thrust-first structure with no filler
- Hamstring-focused days always include a squat-pattern movement

All plans support:
- Versioned snapshots
- Deterministic regeneration
- Diff rendering
- Restore to previous versions

---

## Nutrition System (First-Class, Not an Afterthought)

Nutrition is a full peer of training — not a bolt-on.

**Guaranteed behaviors:**
- Allergens are hard-blocked
- Diet constraints enforced
- No duplicate meals in a plan
- Deterministic calorie & macro math
- Supports maintenance, cut, bulk (0.5 / 1 / 2 lb per week rates)
- No silent reshuffling
- Every regenerate produces a diff with human-readable explanations

### Calorie Repair
If a plan undershoots calories:
- A deterministic post-pass adds safe boosters
- Boosters are diet-safe, allergy-safe, and slot-aware (e.g. no olive oil in oats)
- No random retries, no silent hacks

---

## Macro Aims (Guidance, Not Tracking)

LyftLogic intentionally avoids "tracker" UX.

Instead, it shows:
- Daily calorie aim
- Protein aim: `0.8 g / lb bodyweight`
- Fat target: fixed % of calories
- Carbs: remainder (carb-forward by default)

This gives users clarity without micromanagement.

---

## Versioning & Diffs (Core Feature)

Both training and nutrition support:
- Stateless regeneration
- Versioned snapshots
- Index-stable diffs
- Human-readable explanations

Changes are inspectable, not opaque.

---

## Constraints Model

### Training Constraints
- Equipment bans
- Session length
- Split logic
- Compound caps
- Machine vs free-weight preference

### Nutrition Constraints
- Allergies (fail-closed)
- Diet type
- Calorie targets
- Meal count inference
- Context-preserving regeneration

Rules > preferences everywhere.

---

## Architecture Overview

LyftLogic is built around **explicit state + deterministic transitions**.

1. **Draft generation (untrusted)** — LLM proposes structure only.
2. **Rules engines (authoritative)** — Enforce constraints, normalize outputs, stabilize plans.
3. **Version snapshot** — Immutable record of state.
4. **Diff + explanation** — User-visible, human-readable.

No plan is shown unless it passes validation.

---

## Frontend Philosophy

- Training and Nutrition are separate, first-class pages
- Debug data hidden behind toggles
- Diffs rendered explicitly
- UX favors clarity over density
- No "magic" edits
- Auth-aware nav (email, settings, and sign out when logged in)
- Account settings page — view account info, change password, delete account

---

## Tech Stack

### Backend
- FastAPI (Python)
- SQLite (manual SQL, no ORM)
- Pydantic (strict schemas)
- Deterministic rules engines
- Versioned diff logic
- bcrypt for password hashing
- LLMs used only for drafting

### Frontend
- Nuxt 3 (Vue)
- TypeScript
- REST APIs
- Cookie-based auth (httponly, samesite=lax)
- Dark + purple product UI

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

- No dumbbells → zero leakage
- No barbells → machine/cable substitutions
- 30-minute vs 75-minute sessions
- Beginner vs advanced lifters
- Rest days without filler
- Allergy-safe meal plans
- Calorie changes with explicit explanations

---

## Roadmap

- v1: Deterministic training + nutrition generation ✅
- v2: Accounts + sessions + owner-scoped plan persistence ✅
- v3: My Plans dashboard (training + nutrition unified) ✅
- v4: Auth polish — email verification, password reset, macro reconciliation, focus muscles ✅
- v5: Account settings — change password, delete account, full data cleanup ✅

---

## Project Philosophy

LyftLogic is an engineering-focused system, not a consumer app demo.

The goal is not maximal personalization — it is **predictable, explainable, constraint-aware planning** that users can trust and iterate on.

**Design choices:**
- Determinism is mandatory; novelty is optional
- Every constraint is enforced, not suggested
- Every change is versioned, diffed, and explained
- AI is a tool for drafting, never a source of truth
