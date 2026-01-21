# LyftLogic

LyftLogic is a full-stack **training and nutrition planning system** built around one core idea:

> **AI should draft. Code should decide.**

Instead of trusting model output directly, LyftLogic treats AI as an **untrusted proposal generator** and enforces all important rules **deterministically in code**.  
The result is plans that are **stable, explainable, versioned, and realistic** — not random or vibes-based.

---

## 🚀 What LyftLogic Is (and Is Not)

**LyftLogic is:**
- A deterministic planning system
- Explicitly versioned
- Diff-driven and explainable
- Designed for iteration, not one-off generation

**LyftLogic is not:**
- A “chat until it looks good” app
- A black-box AI fitness tool
- A recommendation engine that resets state on every regenerate

---

## 🧠 Core Design Principles

### 1) AI is never the source of truth
LLMs generate *drafts*.  
All outputs are validated, corrected, and stabilized by deterministic rules engines before being shown to the user.

### 2) Constraints are enforced, not suggested
If a rule exists, it is enforced in code.  
If something violates constraints, it is rejected — not “recommended against.”

### 3) Plans evolve through versions
Plans do not reset.  
They **change**, and every change is:
- deterministic
- diffed
- explained
- reversible

---

## 🏋️ Training System (Realism-First)

Training plans are designed to resemble how experienced lifters actually program.

**Hard rules enforced in code:**
- No cardio before lifting
- No finishers or cooldown fluff
- Simple warmups  
  - 1 lighter warm-up set (~50%) before each lift
- Low-to-moderate volume  
  - Default: 2 working sets per exercise
- Long rest periods  
  - ≥4 min compounds  
  - ≥3 min isolations
- Rep ranges, not prescriptions (e.g. 6–8, 8–12)
- Effort cues instead of RPE
- Core lifts repeat across the week
- Primary compounds are never accessories
- Session length strictly limits exercise count

All training plans support:
- Versioned snapshots
- Deterministic regeneration
- Diff rendering in the UI
- Restore to previous versions

---

## 🥗 Nutrition System (Fail-Closed & Explainable)

Nutrition planning is designed to be **safe, stable, and auditable**.

**Guaranteed behaviors:**
- Allergens are **hard-blocked**
- Diet constraints enforced (vegetarian, vegan, etc.)
- Deterministic calorie and macro math
- Supports maintenance, cut, bulk  
  - 0.5 / 1 / 2 lb per week rates
- No silent changes
- Every regenerate produces:
  - an explicit diff
  - human-readable explanations

Nutrition plans:
- Are generated and regenerated deterministically
- Maintain context across versions
- Never “randomly reshuffle” meals

*(Nutrition editing and persistence are intentionally staged features — see roadmap.)*

---

## 🔁 Versioning & Diffs (Core Feature)

Both **training** and **nutrition** plans support:

- Stateless regeneration
- Versioned snapshots
- Index-stable diffs
- Human-readable explanations

**Example (nutrition regenerate):**
Calories: maintenance changed from 2600 → 2400.
Calories: cut (1 lb/week) changed from 2100 → 1900.
Meal 1 replaced to meet new calorie target.
This makes changes inspectable instead of opaque.

---

## 🧩 Constraints Model

### Training Constraints
- Equipment bans (e.g. no barbells)
- Machine preference
- Session length
- Split logic (Upper / Lower / SHARMS)
- Compound lift caps

### Nutrition Constraints
- Allergies (fail-closed)
- Diet type
- Macro targets
- Meal count
- Regeneration without losing context

**Rules > preferences** everywhere.

---

## 🏗️ Architecture Overview

LyftLogic is built around **explicit state and deterministic transitions**.

### 1️⃣ Draft Generation (Untrusted)
The LLM generates a candidate structure only.

### 2️⃣ Deterministic Rules Engines

#### Training Rules Engine
- Normalizes volume, reps, rest
- Enforces equipment and placement rules
- Stabilizes outputs across edits

#### Nutrition Rules Engine
- Validates meals against allergens
- Computes deterministic macro targets
- Produces versioned snapshots
- Generates index-stable diffs + explanations

No plan is shown unless it passes validation.

---

## 🖥️ Frontend Structure

The frontend intentionally separates concerns:
- **Training** and **Nutrition** live on separate pages
- Plan-level navigation mirrors real product UX
- Diffs are rendered explicitly
- Nutrition is currently read-only (generate / regenerate)

---

## 🛠️ Tech Stack

### Backend
- FastAPI (Python)
- Pydantic (strict schemas)
- OpenAI API (draft generation only)
- Deterministic rules engines
- Versioned diff logic

### Frontend
- Nuxt 3 (Vue)
- TypeScript
- REST API integration

---

## ▶️ Running Locally

### Backend
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

###Backend Runs At
http://127.0.0.1:8000

###Run Tests
pytest -q

###Frontend
cd apps/frontend
npm install
npm run dev

###Frontend Runs At
http://localhost:3000

##Scenarios Handled Correctly
No dumbbells → zero leakage
No barbells → machine/cable substitutions
30-minute vs 75-minute sessions
Beginner vs advanced lifters
SHARMS days without filler
Allergy-safe meal plans
Calorie changes with explicit explanations

##Roadmap (Intentionally Staged)
###Near-Term
Nutrition version persistence
Restore previous nutrition versions
Unified diff history view

###Mid-Term
Nutrition chat edit → apply flow
Deterministic macro calculator
PDF export

###Long-Term
Exercise substitution memory
Workout logging
Performance analytics

##Project Status

LyftLogic is an engineering-focused system, not a consumer app demo.

The goal is not maximal personalization —
it is predictable, explainable, constraint-aware planning that users can trust and iterate on.