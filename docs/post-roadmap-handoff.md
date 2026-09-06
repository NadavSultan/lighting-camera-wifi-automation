# Start here — Cursor implementation handoff

Prepared 2026-09-06 for Lighting Camera WiFi Automation.

## What to open

Start with **`docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md`**. It contains the implementation order, proposed designs, exact file boundaries, test cases, acceptance checks, startup procedure, and a ready-to-copy Cursor instruction.

The recommended order is:

1. BL-003 — polygon drawing feedback.
2. BL-006 — IES assignments across compatible LITE/WIFI/SMART models.
3. BL-002 — clear Wi-Fi coverage display action.
4. BL-008 — CAP workflow, recommended count and selected sites.
5. BL-007 — numerical illuminance labels.
6. BL-004 — movable lighting-results card.
7. BL-005 — fixture-direction arrows.
8. BL-001 — satellite imagery, after provider approval.

## Use on another computer

1. Clone or update [the repository](https://github.com/NadavSultan/lighting-camera-wifi-automation) on `main`. Preserve any local work before updating. The reviewed application commit is `8751714003bf09f39c217a5f26b9fd6056d2927b`; compare newer changes rather than reverting them.
2. Open `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md` in Cursor. The backlog and reproduction records are stored alongside it in this repository.
3. Send the implementation instruction in section 1 of the plan, choosing which item IDs you authorize.
4. The earlier ZIP remains an optional offline snapshot. If using it, extract into a temporary folder first and compare any existing files before copying them; prefer current repository documents over an older snapshot.

The package contains only documentation and diagnostic evidence, not application code, dependencies, customer runtime projects, credentials, or imagery-provider access. Its `SHA256SUMS.txt` permits checking that files survived transfer unchanged.

## Included records

- `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md`: execution plan and Cursor launch instruction.
- `docs/post-roadmap-backlog.md`: eight requests, requirements, risks and live findings.
- `harness/verify/2026-09-06-backlog-live-reproduction.md`: detailed live-test observations and limitations.
- `harness/verify/2026-09-06-backlog-reproduction-observations.json`: API/source-preservation evidence.
- `docs/post-roadmap-handoff.md`: this guide.

## Authorization and current state

The user authorized publishing these documentation and evidence files to GitHub on 2026-09-06. They are maintained in the repository at the paths above; the ZIP is not required when those files are present in your checkout.

The user authorized planning and diagnosis. No implementation is performed or implicitly approved by possessing the plan. The user instruction sent to Cursor should identify the item IDs/designs approved for execution. Satellite requires an additional provider decision; existing phase gates and source-preservation rules remain binding.

No Phase 8 is created. The plan explains the proposed item-based review process because the existing readiness checker only accepts numbered phases. Cursor must not invent a phase number to satisfy it.
