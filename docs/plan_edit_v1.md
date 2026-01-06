# Plan Edit v1 Contract (Phase 1)

Phase 1 makes plans **editable, not regeneratable**.
This doc defines the **v1 editing scope**, schemas, and invariants.

---

## Core idea

**User message → patch proposal → (optional) apply → new plan version saved**

**Invariant:** Any applied edit MUST re-run the deterministic rules engine and output a structurally valid plan.

---

## Supported edits (v1)

v1 supports these intents only:

### 1) Equipment + preference toggles
Hard constraints (bans):
- No barbells
- No dumbbells
- Machines only (optional later if you support it)

Soft preferences:
- Prefer machines
- Prefer dumbbells
- Prefer cables

Rule: **bans always win** over preferences.

### 2) Avoid presets (pain / movement restrictions)
Limited to preset mapping tokens (deterministic):
- avoid shoulders
- avoid overhead press
- avoid deep knee flexion
- etc. (only what you explicitly map)

v1 does NOT do medical interpretation. It only applies known presets.

### 3) Emphasis (priority only)
Examples: emphasize arms / glutes / chest  
Emphasis adjusts selection priority but must not break structure, caps, or safety.

### 4) Global volume/intensity style (safe version of sets/reps edits)
Instead of per-exercise manual overrides, v1 allows **global style knobs**:

- `set_style`: `low | standard | high`
- `rep_style`: `strength | hypertrophy | pump`

All styles are implemented deterministically by the rules engine with hard bounds and time caps.

---

## Explicitly unsupported (NO-GO list)

The chat editor must NOT be able to:

1) **Regenerate** a new plan from scratch  
2) Change number of training days (e.g., “make it 6 days now”)  
3) Change split type / plan identity (Full Body ↔ PPL, “make it strength program”)  
4) Reorder days or exercises (“move legs to Monday”, “put curls before rows”)  
5) Perform specific exercise swaps (“replace X with Y”)  
6) Apply per-exercise manual sets/reps/rest edits (“make bench 5x3”)  
7) Remove or bypass safety constraints (e.g., “ignore knee pain rule”)  
8) Add progression / periodization / week-to-week logic  
9) Add nutrition / meal planning features  
10) Interpret medical conditions beyond preset tokens

If a user asks for something unsupported:
- Return `can_apply = false`
- Provide an explanatory error in `errors[]`

---

## Canonical Patch Schema (v1)

All edits are expressed as a patch. No full-plan rewrite in v1.

```json
{
  "constraints_add": [],
  "constraints_remove": [],
  "preferences_add": [],
  "preferences_remove": [],
  "emphasis": null,
  "avoid": [],
  "set_style": null,
  "rep_style": null
}

