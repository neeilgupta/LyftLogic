# LyftLogic

LyftLogic is a full-stack **strength training planning system** that generates **structured, realistic workout programs** using a hybrid approach:  
**LLM generation + a deterministic rules engine**.

Unlike typical AI fitness apps, LyftLogic does **not** rely on free-form prompt outputs. Every plan is post-processed and enforced against explicit training rules so that the final result is something you would actually run in a real gym.

---

## 🚀 Why LyftLogic Exists

Most AI-generated workout plans fail in predictable ways:

- Random exercise selection every generation
- Cardio mixed into strength warmups
- Inconsistent volume and rest times
- Overuse of abstract metrics like RPE
- Ignoring real gym constraints (equipment, time, preferences)
- “Suggestions” instead of hard enforcement

LyftLogic was built to solve this by treating AI as a **draft generator**, not the final authority.

All important training decisions are enforced programmatically.

---

## 🧠 Core Training Philosophy

LyftLogic follows a strict, realism-first approach:

- **No cardio before lifting**
- **No finishers or cooldown fluff**
- **Simple warmup philosophy**
  - 1 lighter warm-up set (~50%) before each lift
- **Low-to-moderate volume**
  - Default: 2 working sets per exercise
- **Long rest periods**
  - ≥4 minutes for compound lifts  
  - ≥3 minutes for isolation exercises
- **Rep ranges, not prescriptions**
  - 6–8 or 8–12 (movement-dependent)
- **Effort cues instead of RPE**
  - Final set taken close to failure
- **Consistency-first programming**
  - Core movements repeat across the week
  - Emphasis changes, not random exercises
- **Primary compounds are never accessories**
- **Exercise count scales with session length**
  - Shorter sessions = fewer movements
  - Main lifts are never dropped

These rules are **enforced in code**, not suggested.

---

## 🏗️ System Architecture

LyftLogic uses a **hybrid AI + deterministic rules engine**.

### 1️⃣ LLM Draft Generation

The language model produces an initial plan structure based on:
- Experience level
- Days per week
- Session length
- Available equipment
- User notes / preferences

This output is treated as **untrusted input**.

---

### 2️⃣ Deterministic Rules Engine

A custom rules engine post-processes the draft to:

- Enforce movement counts per session
- Normalize sets, reps, and rest times
- Cap compound volume per day
- Enforce session-time exercise limits
- Respect equipment constraints (e.g. *no dumbbells*, *no barbells*)
- Bias exercise selection (e.g. *prefer machines*)
- Prevent invalid placements (e.g. bench as an accessory)
- Remove forbidden content (cardio warmups, RPE, finishers)
- Deduplicate exercises and stabilize outputs

This guarantees **predictable, gym-realistic plans**.

---

## 🧩 Constraints & Preferences (v1)

LyftLogic supports **hard enforcement** of user notes such as:

- **Equipment bans**
  - “No dumbbells”
  - “No barbells”
  - “Prefer machines”
- **Time constraints**
  - Session length directly limits exercise count
- **Split logic**
  - Upper / Lower / SHARMS templates
  - Leg days capped at ≤2 compounds
- **Exercise bias**
  - Machine vs free-weight preference
  - Stable row / press / hinge selection

Notes are treated as **constraints first, preferences second**.

---

## 🛠️ Tech Stack

### Backend
- FastAPI (Python)
- OpenAI API
- Pydantic (strict schema validation)
- Custom deterministic rules engine

### Frontend
- Nuxt 3 (Vue)
- TypeScript
- REST API integration

### Data
- JSON-based plan storage
- Input/output persistence for reproducibility

---

## 📊 Example Scenarios Handled Correctly

LyftLogic reliably adapts plans for cases like:

- “No dumbbells” → zero dumbbell leakage
- “No barbells” → full machine / cable substitution
- Short (30–35 min) vs long sessions
- Beginner vs advanced lifters
- Quad-focused vs hamstring-focused lower days
- Dedicated Shoulders & Arms (SHARMS) days without filler movements

---

## 🔮 Roadmap

### Near-term
- **Plan Editor Chat**
  - Iteratively edit an existing plan instead of regenerating
  - Versioned plan history
  - Explicit constraint enforcement per edit

### Mid-term
- **Macro calculator (deterministic)**
- **AI meal planning driven by macro targets**
- Nutrition education and adherence tools

### Long-term
- Exercise substitution memory
- PDF export
- Simple workout logging
- Performance and speed optimizations

---

## 📌 Status

LyftLogic is an active project focused on **production-quality AI behavior**, not prompt-only generation.

The goal is not maximal personalization —  
it is **trustworthy, editable, constraint-aware training plans**.
