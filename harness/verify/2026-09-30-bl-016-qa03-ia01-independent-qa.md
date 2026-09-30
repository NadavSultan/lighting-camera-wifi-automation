# Independent QA review — 2026-09-30 — BL-016 QA-03 corrective retest

Verdict: PASS

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: product commit `5656da555f9614a2be614738ccf699ce2d58f609`; clean evidence tip `c1d12971897ec2ed74f382f15031f44d4a3cce64`; branch `codex/bl-016-qa03-ia01-independent-retest-2026-09-30`.
- Controlling contract and acceptance IDs: `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md`; Task 10 in `docs/superpowers/plans/2026-09-22-bl-016-camera-pixel-density.md`; `BL016-16` and Task 10 rendered, persistence, failure, and prior-layer checks.
- Reviewer/session independence: fresh production browser session and isolated temporary API project on the exact clean evidence tip. The product commit is an ancestor of the evidence tip. The prior FAIL report was read from its preserved branch and not modified.
- Review scope: production 74-pole KML import, camera-density overlap hit testing and popup content at multiple locations/multiplicities, Standard/Satellite map behavior, popup scrolling/dismissal, stale/reopen behavior, controlled request validation, source preservation, and visible Phase 3/7 regressions.
- Non-goals and excluded phases: no product edits, merge, BL-016 acceptance, master-gate decision, phase seal, or post-roadmap work. The prior FAIL report remains an immutable historical record; this report supplies new evidence that closes its `QA03-IA-01` finding for gate review.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Exact HEAD/product commit, clean status, controlling contract, prior FAIL and corrective handoff | PASS; product commit is in the reviewed tip; starting product tree clean; no product source edits |
| Deterministic verification | Backend/frontend tests, catalogs, typecheck/lint, configured production build, schema/source freshness | PASS; details below. Frozen pnpm reinstall was blocked by Windows access denied while removing existing `frontend/node_modules`; direct installed entry points were used successfully |
| Acceptance-matrix review | `BL016-16` and Task 10 workflows | PASS; four distinct popup multiplicities/positions matched persisted regions exactly |
| Rendered/manual workflow | Production browser, 74-pole source, Standard/Satellite, popup, scroll/dismissal, stale/reopen | PASS; one popup per click; Satellite attribution and density overlay remained visible; stale state survived JSON reopen |
| Source/prior-phase regression review | Original source hash, existing-pole boundary, Phase 3 geometry and Phase 7 preview | PASS; unchanged KML hash, 148 valid camera footprints, report preview `Complete with warnings` |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| `BL016-16`: one click on a density overlap shows actual multiplicity, complete contributor set, persisted winner and displayed band/range | Clicked four rendered overlap regions at distinct map positions; for each, compared popup fields against saved `camera_pixel_density.result.overlap_regions` and winning camera band data | Multiplicities 4, 6, 5, and 9 each yielded exactly one matching persisted overlap region when matching contributor IDs, winner, and winning band. Ranges were 15–20, 10–15, 20–30, and 20–30 px/face respectively. Popup data is itemized in `2026-09-30-bl-016-qa03-ia01-browser.json`. | PASS |
| Task 10: Standard and Satellite render and inspect consistently | Switched between both map backgrounds and clicked the same overlap point in each | Standard attribution showed OpenStreetMap contributors. Satellite showed aerial imagery and visible EOX Cloudless attribution. The same 4× point returned the same winner, four contributors, `px-face-15`, and 15–20 px/face on both backgrounds. | PASS |
| Task 10: popup readability, scroll, and dismissal | Visually inspected popup and scrolled its content area; closed with Close popup | Popup is bounded within the map above its caption, uses readable dark text on a light surface, scrolls through the full contributor set to the freshness and disclaimer text, and disappears on close. Accessibility state contained a single popup container and one close control after each tested click. | PASS |
| Task 10: stale and reopen persistence | Changed maximum visible distance from 50 m to 40 m, saved the project, reopened the saved project JSON through Open Project, and returned to Camera | Reopened project showed 40 m, `Stale — recalculate required`, and disabled/unchecked density layer. Restored 50 m and recalculated successfully; final UI returned to Current. | PASS |
| Task 10: controlled failure | Submitted the saved full project JSON to the camera-density calculate route with lower plane 3 m and upper plane 2 m | API returned HTTP 422 with `lower projection height must be less than upper projection height`; project JSON SHA-256 was identical before and after (`6810fb7d9d2c05f944d419bb105e4100f6338acbb769e4dcdd5dc1b8eaf0b051`). This verifies request validation and no mutation, not an internal calculation exception. | PASS |
| Source preservation and existing-pole boundary | Imported `Input/Miracle_Mile_Lighting_Poles.kml` in existing-pole mode; hashed repository and isolated copied source | Both SHA-256 values: `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`. UI showed 74 imported source poles, customer coordinates locked, and no generated poles. | PASS |
| Prior Phase 3 camera geometry | Inspected Camera tab after import and calculation | 148 valid camera footprints; 4,953 camera footprint overlap pairs; 132,360,531.5 m² summed pairwise overlap. Camera and lens assignments remained IMX477 / JL-LN037 3.56 mm; two-camera geometry remained present. | PASS |
| Prior Phase 7 report preview | Inspected report package panel in production UI | Existing preview status remained `Complete with warnings`; warnings/dispositions remained available. No report was generated or downloaded. | PASS |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `..\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider` from `backend/` | Evidence tip `c1d12971897ec2ed74f382f15031f44d4a3cce64` | Exit 0; 364 passed | One Starlette/httpx deprecation warning |
| `..\\.venv\\Scripts\\python.exe scripts\\validate_engineering_data.py` from repository root | Evidence tip | Exit 0 | Eight engineering catalogs/source hashes validated |
| `corepack pnpm install --frozen-lockfile` from `frontend/` | Evidence tip | Failed; access denied removing existing modules directory | Environment limitation. `pnpm-lock.yaml` unchanged; direct package entry points and configured build ran from installed dependencies |
| `corepack pnpm run test` from `frontend/` | Evidence tip | Exit 0; 112 passed | Existing installed dependencies |
| `node node_modules/typescript/bin/tsc --noEmit` from `frontend/` | Evidence tip | Exit 0 | Direct TypeScript entry point |
| `node node_modules/eslint/bin/eslint.js . --ignore-pattern dist --ignore-pattern .next` from `frontend/` | Evidence tip | Exit 0 | Direct ESLint entry point |
| `node node_modules/vinext/dist/cli.js build` from `frontend/` with configured API and Satellite public variables | Evidence tip | Exit 0 | Advisory output included chunk size >500 KB and route/plugin timing notices |
| `node --test tests/satellite-production-bundle.integration.mjs` from `frontend/` with configured Satellite public variables | Evidence tip | Exit 0; 1/1 passed | Verified configured production bundle values |
| `..\\.venv\\Scripts\\python.exe -m scripts.export_schema` from `backend/` | Evidence tip | Exit 0 | Follow-up `git diff --check`, schema diff, and source/lockfile diff were clean |
| Real-browser production workflow at `http://127.0.0.1:3070/`, API at `http://127.0.0.1:8070/` | Product `5656da555f9614a2be614738ccf699ce2d58f609`, isolated project `8719e736-741b-49f6-8048-f75d16d6c54e` | PASS | Import, calculated result, popup comparisons, basemap switching, popup scroll/close, stale save/reopen, and recovery calculation completed |
| Controlled invalid-profile `POST /api/projects/{project_id}/camera-pixel-density/calculate` | Same product and isolated project | HTTP 422; saved project unchanged | Validation response and before/after project SHA are recorded above |

Historical implementation evidence guided setup only; it does not substitute for the checks recorded here. The browser was visually observed in-session; no screenshot file or standalone browser-console-log artifact was saved. The CUA browser interface did not expose console log collection in this retest. This limitation does not affect the direct popup/persisted-result comparisons or deterministic verification above.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| `QA03-IA-01` | Major | `BL016-16`; four distinct map positions and multiplicities compared with saved overlap data, on Standard and Satellite | Corrected behavior reports exactly one popup with full persisted multiplicity/contributors/winner/band and the corresponding stored band interval. The issue in the preserved 2026-09-29 FAIL report was not reproduced. | No further correction identified by this retest; retain the prior FAIL report and use this report for master-gate review. |

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [x] Every mandatory acceptance item in this review scope disposed as PASS or recorded as a blocking finding.
- [x] Required deterministic and rendered checks completed on the exact reviewed commit.
- [x] Source preservation, migration, prior-phase regressions, and later-phase exclusion verified.
- [x] Verdict is supported without relying on unverified claims.

## Recovery protocol

1. Preserve the prior FAIL report, this report, and exact reviewed commit identity.
2. No product source changed during this retest. The temporary project was restored to the valid 50 m profile and recalculated after the stale/reopen check.
3. Any later product change invalidates affected QA observations and requires retesting that exact commit.
4. Resume from the evidence recorded here.

## Allowed stopping conditions

QA is complete for the recorded scope. This PASS is independent evidence only; it does not accept BL-016, create a phase seal, authorize a later phase, or replace the master gate.

## Verdict and next gate

- Verdict: PASS for `QA03-IA-01` corrective retest and the Task 10 checks listed above.
- Open findings: none from this retest. The earlier FAIL report remains preserved as the historical finding record.
- Master gate eligibility: not decided here; the master gate and remaining BL-016 acceptance evidence have not been run by this retest.
- Exact next action: use this report as evidence in the existing BL-016 master-gate process; do not infer phase acceptance or create a seal from this QA PASS alone.
