# NIR-01 completion note

Date: 2026-08-15

Scope: Phase 2 low-severity failed-IES-upload feedback only.

- A rejected upload now refetches the open catalogs immediately, so the backend-retained invalid/unsupported record appears without reloading.
- Structured API detail is reduced to its concise human-readable `message` rather than rendered as raw JSON.
- The failed record remains inactive; its activation control is disabled, it is excluded from the active-valid association selector, and clearing the selector disables association and default actions.
- Backend persistence and validation behavior are unchanged.
- Focused frontend regression coverage and a no-reload manual browser workflow passed.

Both independent QA reports remain unchanged. Phase 3 and unrelated functionality were not started.
