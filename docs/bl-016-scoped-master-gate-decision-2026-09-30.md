# Scoped master gate — BL-016 camera pixel-density map

Date: 2026-09-30

Decision: **PASS — BL-016 / WA-09 accepted at the scoped post-roadmap gate.**

This decision applies to product commit `5656da555f9614a2be614738ccf699ce2d58f609`, reviewed through independent-QA evidence commit `867cd72a407ade4636c3c7aa317346c663bc82a2`. It closes the authorized BL-016 item only. It does not create Phase 8 or a phase seal, or authorize BL-019/BL-020, merge, or push.

## Controlling evidence

- Approved design and plan: `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md` and `docs/superpowers/plans/2026-09-22-bl-016-camera-pixel-density.md`.
- Original `BL016-01`–`BL016-20` implementation matrix: `harness/verify/2026-09-22-bl-016-camera-pixel-density-verification.md`. The 2026-09-24 master correction, QA-01 CORS correction, QA-03 Satellite correction, and `QA03-IA-01` overlap correction supersede only the affected earlier evidence. Their reports and work records remain in `harness/verify/` and `harness/phases/`.
- Final correction handoff and clean readiness: `harness/verify/2026-09-29-bl-016-qa03-ia01-independent-qa-handoff.md` and its readiness manifest. The verifier returned `IMPLEMENTATION READINESS: PASS` against product commit `5656da55` on the clean QA branch.
- Independent QA PASS: `harness/verify/2026-09-30-bl-016-qa03-ia01-independent-qa.md` and companion browser JSON. The preserved 2026-09-29 QA FAIL remains historical; its Major `QA03-IA-01` finding is closed by the new retest.

## Acceptance disposition

`BL016-01`–`BL016-13` are supported by the full backend suite, analytic/migration/limit/API tests, generated-schema freshness, engineering validator, and the isolated live harness. `BL016-14`–`BL016-17` are supported by frontend tests, the configured production build, implementation browser evidence, and independent QA's Standard/Satellite, overlap, stale/reopen, and controlled-validation workflows. `BL016-18`–`BL016-20` are supported by the report-package and prior-phase regressions, source preservation, full deterministic checks, live evidence, readiness PASS, and independent QA PASS. No acceptance ID remains open at this gate.

The final overlap correction uses one map-click inspection path, resolves MapLibre-serialized contributor IDs, and displays the persisted winner, complete contributors, multiplicity, and winning band interval. Independent QA compared four distinct 4×, 5×, 6×, and 9× points with exactly one persisted region each, obtained one popup per click, and confirmed consistent inspection on Standard and Satellite. Earlier QA observed 2×–11× labels; focused 2× helper coverage and backend two-/three-camera overlap tests remain applicable. The exact 2×/3× interactive click cases were not separately captured on the final commit, so no such direct browser observation is claimed.

## Fresh master verification

Checks below ran against clean reviewed HEAD `867cd72a407ade4636c3c7aa317346c663bc82a2`, which contains product commit `5656da55` with no later product edits:

- Backend: `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` from `backend/` exited 0; the independent QA run recorded 364 passing tests. The known Starlette/httpx deprecation warning remained non-failing.
- Engineering-data validator exited 0 for eight catalogs and supplied-source hashes. The KML SHA-256 was `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`.
- Frozen frontend install, `corepack pnpm install --frozen-lockfile`, exited 0 after rerunning outside the restricted sandbox; lockfile was unchanged. This resolves the independent QA report's Windows access-denied install caveat. The sandboxed first master attempt could not reach npm and was stopped, not counted as a pass.
- `corepack pnpm run test`, `typecheck`, `lint`, and the configured `build` exited 0; 112 frontend tests and the integrated Satellite production-bundle test passed. The build retained only non-failing Vinext plugin-timing, large-chunk, and route-classification advisories. Initial sandboxed direct build could not write Vite's ignored temporary file; the successful permitted rerun is the gate evidence.
- `..\.venv\Scripts\python.exe -m scripts.export_schema` exited 0; `git diff --exit-code -- schemas Input frontend/pnpm-lock.yaml`, `git diff --check`, and final Git status were clean.
- The isolated production live runner completed 12/12 assertions at the reviewed HEAD. Its exact output is preserved in `harness/verify/2026-09-30-bl-016-master-live.json`; it recorded zero Chrome shell console/page errors, the exact 74-pole source hash, atomic 422 failure, stale/recalculate lifecycle, KML export, and Phase 7 report generation.
- The independent production-browser retest observed four matching multi-camera popups, visible Satellite imagery/EOX attribution, popup scroll/dismissal, stale save/reopen, and unchanged project bytes after invalid-profile rejection.

The independent QA browser did not retain a screenshot or standalone console log, and its controlled failure exercised request validation rather than an injected internal exception. The implementation browser record on the exact product commit captured no console warnings/errors; the master live harness captured zero shell errors. Backend tests cover unexpected/atomic failure paths. These evidence limits are recorded rather than represented as direct independent browser observations.

## Boundary and next action

The source KML, `Input/`, frozen catalogs, accepted Phase 3 geometry, prior-phase seals, and frontend lockfile are unchanged. The final QA branch contains only evidence commits after the product commit. No merge or push has been performed by this gate.

BL-016 is accepted at this scoped gate. Reconcile the execution indexes to this decision and make one documentation-only gate commit. Integrate or push the approved product/evidence history only after a separate explicit request; keep BL-019/BL-020 and any other post-roadmap work gated. No Phase 8 or BL-016 phase seal exists or is required.
