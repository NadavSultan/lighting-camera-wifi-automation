# Phase 4 master gate decision

Date: 2026-08-26
Decision: **PASS — Phase 4 is formally closed**
Accepted implementation through: `a313a6c617fa91c9bfd3eff85842205851954717`

## Decision

Phase 4, the explicitly authorized simplified direct-lighting engine, is accepted and formally closed. All seven Phase 4 integration-review findings have independent passing evidence. Phase 5 conceptual Wi-Fi and every later phase remain unauthorized and unstarted; this decision does not authorize them.

## Controlling evidence

- `docs/phase-4-integration-review-and-qa.md` identified P4-IR-01 through P4-IR-07 and failed the original implementation.
- `docs/phase-4-corrective-retest-report.md` independently passed P4-IR-01, P4-IR-02, P4-IR-03, P4-IR-04, P4-IR-06, and P4-IR-07 while leaving P4-IR-05 open.
- `docs/phase-4-final-focused-retest-report.md` confirmed that syntactically invalid CRS input was controlled but geographic and projected non-metre CRS values remained incorrectly accepted.
- Commit `a313a6c` enforced the shared non-null project engineering CRS contract: parseable, projected, and metre-axis based.
- `docs/phase-4-final-p4-ir-05-independent-retest-2026-08-26.md` independently passed P4-IR-05 across save/update, open, invalid stored get, bulk configuration, camera recalculation, and lighting calculation paths.

## Accepted verification

- Complete backend suite: 122 passed with one known non-failing Starlette/httpx deprecation warning.
- Independent focused CRS tests: 14 camera/CRS tests and one lighting invalid-CRS test passed.
- Engineering/source validator: all seven catalog/schema pairs and supplied-source hashes passed.
- Invalid, geographic, and projected non-metre CRS inputs returned controlled 422 responses and preserved stored state; valid `EPSG:32617` and nullable blank-project behavior remained operational.
- The previously completed production-rendered Phase 4 workflow, frontend tests, strict TypeScript, ESLint, and production build remain applicable because the final P4-IR-05 correction changed no frontend or generated-contract source.
- Customer poles, coordinates, raw coordinate text, supplied files, frozen catalogs, camera priority areas, and lighting calculation areas remained unchanged and separate.

## Accepted limitations

Phase 4 remains a simplified far-field, direct horizontal illuminance model. It is not independently validated against AGi32 or another professional photometric reference tool, does not model terrain or occlusion, and makes no standards-compliance claim. Fixture-to-IES selection remains explicit, the approved orientation assumptions remain visible, and both supplied Solitaire files retain the documented 50 W decision and internal-identifier warning.

These limitations are explicit product boundaries, not open Phase 4 gate failures.

## Phase boundary

Phase 4 is closed at the accepted scope. Phase 5 conceptual Wi-Fi requires a separate explicit user authorization before planning or implementation. Existing-pole mode remains mandatory, and no later phase may generate, move, optimize, redistribute, or delete customer poles without explicit authorization.
