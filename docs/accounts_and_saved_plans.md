# Accounts + Saved Plans (Not Implemented Yet)

This document outlines the future shape of user accounts and saved plans. It is a design note only.

## Proposed Data Model
- `users` table
  - `id`, `email`, `created_at`
- `plans` table (training + nutrition)
  - `id`, `owner_id`, `plan_type`, `created_at`, `updated_at`
- Version tables stay as-is, but gain `owner_id` or join through `plans`.
  - Training versions remain deterministic snapshots + diffs.
  - Nutrition versions remain deterministic snapshots + diffs.

## API Endpoints (To Add Later)
- `GET /me` to fetch the authenticated user.
- `GET /plans` to list saved plans for the current user.
- `POST /plans` to save a plan snapshot.
- `GET /plans/:id` to fetch a saved plan with versions.

## Frontend Notes
- Add a user store to hold the current user and demo mode.
- Add a saved plans list page with basic filtering by plan type.
- Keep version history per plan and surface diff/restore UI from existing components.

## Status
Not implemented yet.
