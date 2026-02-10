# Phase 5 — Accounts & Persistence

## Why Phase 5 is the biggest unlock

Phase 5 introduces user accounts and persistent plans.

This is the largest functional unlock since v1 because it changes LyftLogic from a
single-session generator into a system users can return to.

Specifically, this enables:
- Users can leave and come back later without regenerating plans
- Version history becomes meaningful instead of transient
- Training and nutrition plans gain parity in ownership and lifecycle
- A foundation for future UX improvements without refactors

Importantly, Phase 5 does not change plan generation logic.
It only introduces ownership and persistence.

---

## Core invariants

These rules must hold true once Phase 5 is implemented.

- Plans are immutable once versioned
- Any change creates a new plan version
- Restoring a plan creates a new version (no rollback mutation)
- No plan changes occur without explicit user action
- Generation remains deterministic for identical inputs
- Persistence never silently alters plan content

These invariants preserve trust and debuggability.

---

## Data model sketch (conceptual)

This is a conceptual model, not a final schema.

### users
- id
- email
- created_at

### plans
- id
- owner_id (nullable for demo plans)
- type (`training` | `nutrition`)
- created_at

### plan_versions
- id
- plan_id
- version
- snapshot_json
- created_at

Notes:
- `snapshot_json` stores the full plan state at that version
- Version numbers are monotonic per plan
- Demo plans may exist without an owner_id

---

## API shape (future)

Authentication:
- `POST /auth/login`
- `GET /me`

Plans:
- `GET /plans`
- `GET /plans/:id`

Versions:
- `POST /plans/:id/versions`
- `POST /plans/:id/restore`

Notes:
- Restore semantics match current demo behavior
- No implicit overwrites
- All mutations result in new versions

---

## Frontend implications

Introducing accounts implies the following UI changes:

- Login gate before accessing saved plans
- A "My Plans" page listing all user plans
- Separate training and nutrition plans under the same account
- Version list per plan
- Restore behavior identical to current version restore

The existing demo flow remains valid for unauthenticated users.

---

## Migration notes (demo → accounts)

Demo plans created without an owner_id may be claimed by a user on first login.

No data migration is required to begin Phase 5.
Ownership can be attached lazily.

---

## Explicit non-goals

Phase 5 explicitly does NOT include:
- Social features
- Plan sharing
- AI chat or conversational edits
- Automatic plan modifications
- Background recomputation
- Performance optimization

This phase is about ownership and persistence only.
