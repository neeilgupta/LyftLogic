# LyftLogic

LyftLogic is a full-stack workout planning system that generates **structured, consistent strength training programs** using a combination of LLM generation and deterministic rule enforcement.

Unlike typical AI fitness apps, LyftLogic prioritizes **training realism**: consistent exercise selection, appropriate volume, long rest periods, and clear constraints — not generic or random workouts.

---

## 🚀 Why LyftLogic Exists

Most AI-generated workout plans suffer from the same issues:
- Random exercise selection every day
- Cardio mixed into strength warmups
- Inconsistent volume and rest times
- Overuse of abstract metrics like RPE
- No respect for real gym constraints (equipment, soreness, preferences)

LyftLogic was built to solve these problems by enforcing **explicit training rules** on top of AI outputs.

---

## 🧠 Core Design Principles

LyftLogic follows a strict training philosophy:

- **No cardio before lifting**
- **Simple, non-timed warmups**
- **No finishers or cooldown fluff**
- **1 warm-up set + 1–3 working sets**
- **Long rest periods**
  - ≥4 minutes for compound lifts  
  - ≥3 minutes for isolation exercises
- **Rep recommendations only** (6–8 or 8–12)
- **Effort-based cues instead of RPE**
- **Consistency-first programming**
  - Core exercises are reused across weeks
  - Volume and emphasis change, not movements
- **Primary barbell compounds are never accessories**
- **Exercise count scales with session length**

These rules are enforced programmatically — not left to the language model.

---

## 🏗️ System Architecture

LyftLogic uses a **hybrid AI + rules engine architecture**:

### 1. LLM Generation
- Generates an initial workout structure based on:
  - Experience level
  - Equipment
  - Session length
  - Preferences and soreness constraints

### 2. Deterministic Rules Engine
- Post-processes the model output to:
  - Enforce movement counts per session
  - Normalize sets, reps, and rest times
  - Respect barbell vs machine preferences
  - Prevent invalid exercise placement (e.g. bench as an accessory)
  - Remove forbidden content (cardio warmups, RPE, finishers)

This ensures outputs remain **stable, predictable, and gym-realistic**.

---

## 🛠️ Tech Stack

**Backend**
- FastAPI (Python)
- OpenAI API
- Pydantic (strict schema validation)
- Custom deterministic rules engine

**Frontend**
- Nuxt 3 (Vue)
- TypeScript
- REST API integration

**Data**
- JSON-based plan storage
- Input/output persistence for reproducibility

---

## 📊 Example Constraints Handled

LyftLogic correctly adapts programs for cases like:
- “Prefer barbell compounds”
- “Prefer machines only”
- “Mild knee pain”
- “Limited session time”
- Beginner vs advanced lifters
- Fat loss vs muscle/strength focus

---

## 🔮 Future Work

- Weekly progression tracking
- Deload logic
- User feedback loop (auto-adjust volume)
- Exercise substitution memory
- Mobile-friendly UI

---

## 📌 Status

LyftLogic is an active, evolving project focused on **production-quality AI behavior**, not prompt-only generation.
