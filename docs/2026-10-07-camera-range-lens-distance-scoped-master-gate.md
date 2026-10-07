# Scoped master gate — camera range, lens details, and distance UX

Date: 2026-10-07

Decision: **PASS — the separately approved camera UX correction is accepted at this scoped post-roadmap gate.** This decision applies to product commit `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`, reviewed through independent-QA evidence tip `24a10b1667235f4bb242c701341a90f916e32afd`. It does not reopen or alter the accepted Phase 3 or BL-016 calculation gates.

## Authority and scope

- Approved design: `docs/superpowers/specs/2026-10-04-camera-range-lens-distance-design.md`.
- Approved execution plan and UX-01–UX-09 matrix: `docs/superpowers/plans/2026-10-04-camera-range-lens-distance.md`.
- Implementation work record and verification: `harness/phases/2026-10-04-camera-range-lens-distance.md` and `harness/verify/2026-10-04-camera-range-lens-distance-summary.md`.
- Independent QA: `harness/verify/2026-10-04-camera-range-lens-distance-independent-qa.md`, **PASS**, no open product findings, with production Chrome and 74-pole evidence.

The product diff from base `98ac861e5eb9bc1587604f3f43be61908baabfb2` adds a read-only projected-metre measurement endpoint, bounded preview of the existing BL-016 projection envelopes beneath the density raster, exact pinned camera/lens specification cards, and transient two-click measurement UI. It removes only the uncapped Phase 3 FOV/overlap map fills and their primary controls; the persisted Phase 3 geometry and metrics remain intact. No product files changed after `fb1c522f` through the reviewed QA tip.

## Acceptance disposition

UX-01–UX-09 are supported by the implementation tests and the independent QA matrix. The QA run directly exercised 50/25/75 m preview recalculation, below-threshold preview without invented density colour, historical pinned specifications, projected 50 m measurement, clear/Esc/error/race behavior, drawing exclusivity, source-preserving export/reopen, and responsive map controls. The QA report explicitly separates recovered setup issues from product findings. Its downloaded-file observer timeout was resolved by validating and reopening the actual file; concurrent whole-request hashing is not treated as proof of endpoint non-persistence. No acceptance ID remains open.

## Fresh master verification

On clean reviewed HEAD `24a10b16`, the master reran:

- Backend `python -m pytest -q -p no:cacheprovider` with a fresh unique pytest base directory, before and after schema export: both exited 0. Non-failing Starlette/httpx and AnyIO deprecations remained.
- `scripts/validate_engineering_data.py`: exit 0; eight catalogs and supplied-source hashes validated.
- `python -m scripts.export_schema`: exit 0. Generated schemas, `Input/`, and frontend lock/workspace files had no working-tree diff afterward; `git diff --check` was clean.
- Frontend `corepack pnpm run typecheck`, `lint`, configured EOX Satellite production `build`, then `test`: all exited 0; 126 frontend tests passed and the configured Satellite bundle assertion passed. Build emitted non-failing Vinext/Vite plugin-timing, chunk-size, and route-classification advisories.
- The implementation-readiness verifier on clean QA tip: exit 0, six milestones and nine acceptance criteria. This is supporting implementation evidence, not the acceptance mechanism.

The supplied KML SHA-256 remained `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`. Base-to-product comparison found no changes to `Input/`, data, accepted Phase 3 or BL-016 calculation engines, frozen catalogs, dependencies, four non-OpenAPI schemas, or prior seals. The independent production-browser QA and 20/20 isolated live API assertions supply rendered/runtime evidence; the master did not claim a second browser session.

## Boundary and next action

This is a scoped post-roadmap acceptance, not a numbered phase. No Phase 8, phase seal, merge, push, or later backlog implementation is authorized by this decision. Preserve the product/QA/master evidence history; integrate or push it only on a separate explicit request.
