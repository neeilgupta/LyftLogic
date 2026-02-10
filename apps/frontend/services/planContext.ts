// planContext.ts
export const DEMO_MODE = true

// Returns the current user's ID once accounts are implemented.
// In demo mode, plans are created without an owner.
export function getCurrentUserId(): string | null {
  return DEMO_MODE ? null : "future-user-id"
}
// owner_id will be attached once Phase 5 (accounts) is implemented
