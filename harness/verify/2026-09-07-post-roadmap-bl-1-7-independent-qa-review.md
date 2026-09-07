# Independent QA review — 2026-09-07 — Post-roadmap BL Stages 1–7

Verdict: **PASS**

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: **dirty worktree** on branch `codex/bl-006-ies-associations` at HEAD `71d4d5248f5460268b9993e9f405693b8aa2434e`. Product implementation is **uncommitted** (tracked modifications + untracked product/harness files). Identity is this worktree, not a clean implementation commit.
- Reviewed application ancestor: `8751714003bf09f39c217a5f26b9fd6056d2927b` is an ancestor of HEAD (`merge-base --is-ancestor` exit 0). Docs tip `71d4d52` was **not** rolled back.
- Controlling contract, phase record, and acceptance IDs: `docs/post-roadmap-backlog.md`; `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md` Tasks 1–7; Stage 0 `harness/phases/2026-09-07-stage-0-prep.md`; per-item records `harness/phases|logs|verify/2026-09-07-bl-003` through `bl-005` (and `bl-002`, `bl-006`, `bl-008`, `bl-007`, `bl-004`). Item process (no Phase 8; readiness verifier not used).
- Reviewer/session independence: fresh Independent QA session. Implementer verification summaries treated as claims until re-run/re-inspected on the live dirty tree.
- Review scope: Stages 1–7 only — BL-003, BL-006, BL-002, BL-008, BL-007, BL-004, BL-005. File-boundary, source-preservation, schema/API, deterministic suites, helper/acceptance matrices, and rendered-source/production-build evidence.
- Non-goals and excluded phases: **no** BL-001 / satellite; **no** OBS-01 correction; **no** Phase 8; **no** merge, seal, or scoped master PASS; **no** product implementation except in-scope defect repair (none performed).

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Branch/HEAD `71d4d52`; ancestor `8751714`; dirty Stages 1–7 tree preserved; BL-001 gated; no Phase 8 | PASS |
| Deterministic verification | Frontend typecheck/lint/build/test; full backend pytest with short `%TEMP%` basetemp; focused BL-005/2/4/5/6 tests; live OpenAPI equals `schemas/openapi.json`; `project.schema.json` hash unchanged vs HEAD; engineering-data validator; `Input/` clean | PASS |
| Acceptance-matrix review | Every `BL003-*` … `BL005-*` ID inspected against helpers, wiring, and current commands | PASS |
| Rendered/manual workflow | Production frontend test includes SSR/source-string coverage (49 tests). **Live MapLibre browser matrix from the plan was not independently executed** (no Playwright / browser MCP in this environment) | deferred (labeled) |
| Source/prior-phase regression review | `Input/` diff empty; Phase 1 catalogs untouched; Phase 2/4/5/6/7 suites inside backend **297 passed**; no Wi-Fi/CAP/lighting equation changes observed | PASS |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| BL003-01 visible 0/1/2/3-point feedback in all three tools | Helper tests + map source/layer registration | `polygon-draft.test.mjs`; `EngineeringMap.tsx` `addDraftSourcesAndLayers` for `priority`/`calculation`/`wifi` (vertices, 4 px edge + 6 px casing, fill ≥3, dashed preview) | PASS |
| BL003-02 cursor segment + map-local finish/cancel guidance | Code + CSS + helper guidance copy | `polygonDraftGuidance`; overlay `polygon-draft-guide` with vertex count, Finish disabled `<3`, Cancel; `pointer-events: auto` + `stopPropagation` | PASS |
| BL003-03 cancel/invalid redraw never replaces saved rings or source | Code review of finish/cancel paths | Invalid `finish*` catches and returns without `mutateProject`; cancel clears draft only; redraw starts empty while stored rings remain until validation | PASS |
| BL003-04 pan/zoom/selection and save/reopen remain usable | Frontend gates + drawing click isolation | Layer clicks no-op while `isDrawing()`; no backend/schema change for this item; typecheck/lint/build/test exit 0 | PASS |
| BL006-01 one file shows three simultaneous compatible assignments | Helper + Catalog UI + Phase 2 API unchanged | `associationRows` three Phoenix checked; `IesAssociations` “Assigned models” grouped by family; `test_phase2_catalogs.py` green | PASS |
| BL006-02 one removal preserves the others | UI uses existing DELETE pair endpoint; helper file-scoped rows | `removeIesAssociation`; checkbox from API after refresh, not optimistic | PASS |
| BL006-03 invalid/family restrictions and source hashes intact | Backend Phase 2/4 + UI disable | Invalid/inactive files `canEdit=false`; no frontend hash allowlist; `validate_engineering_data.py` PASS; `Input/` unchanged | PASS |
| BL006-04 defaults/pins change only via explicit actions | Code review | Separate “Set default”; no pole auto-adopt | PASS |
| BL002-01 calculation offers explicit display action | Helper + workspace wiring | `wifiMapState` hidden vs visible; `WifiMapSummary` “Show coverage on map” calls `toggleLayer("wifi_coverage", true)` after result exists; calculate does **not** auto-enable | PASS |
| BL002-02 all current circles at recorded extents | Map layers; no engine change | Existing circle GeoJSON; cyan outline + dark casing; fill opacity 0.12 | PASS |
| BL002-03 no-area/empty/stale states are clear | Helper + sidebar/overlay | Distinct `not-calculated`/`empty`/`hidden`/`visible`; empty copy for zero eligible fixtures; overlay unmounts when result is null (stale); boundary gap message retained | PASS |
| BL002-04 statistics, disclaimers, source, default-off intact | Code + Phase 5 pytest | Default-off preserved; expandable stats + disclaimer; `test_phase5_wifi_coverage.py` 15 passed | PASS |
| BL008-01 entry and next step discoverable | Toolbar + panel | “CAP Planning” + “Recommend CAP”; panel `id="cap-planning-panel"`; actions explained | PASS |
| BL008-02 blockers explain reason and input location | Helper + Review input | Readable labels/focus ids; `reviewCapInput` focuses existing controls; unknowns remain unknown | PASS |
| BL008-03 count/list/map agree with current result | Helper uses recommendation IDs; map locate uses stored candidate coordinates | `capResultSummary` selected length from `cap_recommendations.selected_candidate_ids`; “Show selected sites on map” enables existing layers and fits bounds; Locate pans only | PASS |
| BL008-04 operations/constraints/provenance/invalidation unchanged | Phase 6 pytest + reuse of `phase6-cap-workflows` | Same `runCap` save-then-calculate/validate/recommend; provenance expandable; `test_phase6_cap_planning.py` 66 passed | PASS |
| BL008-05 no fixture movement, inferred candidates, or operational approvals | Diff/code | No CAP service/model/schema edits; locate/show do not mutate candidate coordinates | PASS |
| BL007-01 each displayed point has a value, not just color | Canvas labels + no thinning | `LightingPointLabels` draws every in-viewport point; off-canvas cull only; “Zoom in to separate point values” without hiding | PASS |
| BL007-02 values/units match maintained results; storage precision preserved | `formatLux` tests; labels from stored field | Spec cases `0.00` / `12.35` / `0.0012` / `—`; legend “maintained illuminance (lx)”; no calculation/schema change | PASS |
| BL007-03 labels track map motion without blocking interaction | RAF + CSS | move/resize/zoom/rotate/pitch; `pointer-events: none` | PASS |
| BL007-04 stale/deleted points and labels disappear together | Points derived from current `lighting_calculations.results` and `calculation_points` layer | Invalidation clears results → empty label set | PASS |
| BL004-01 success opens correct-area results beside drawing endpoint | Workspace calculate + `ringAnchorLngLat` | `calculateSelectedArea` opens card; last draft vertex captured before clear; reopen fallback = final non-closing ring vertex | PASS |
| BL004-02 freely movable, recoverable card with correct units/ratios | Helper + card UI | `clampCard` 512/412 and margin tests; header drag + Reset/Close; Eavg/Emin/Emax lx; named Emin/Eavg and Emin/Emax; null → `—` | PASS |
| BL004-03 current/stale/failed state is truthful | Card + session state | Missing result → unavailable copy; failed calculate does not `setProject`; delete area closes card; session-only position | PASS |
| BL004-04 no schema, export, source, or calculation mutation | Diff | No `project.schema.json` change; no lighting-engine edit | PASS |
| BL005-01 visible directions for every configured lighting fixture | Backend preview tests + map canvas | Configured lighting-capable poles in `directions`; 24 px colored arrows; inactive muted | PASS |
| BL005-02 correct projected-north / map-bearing conversion | Backend N/E/S/W + convergence test; `screenArrow`; map.project on move/rotate | `projected_direction_endpoint(100,200,90)==(101,200)`; CRS sample not geographic-only; screen vector after backend metres | PASS |
| BL005-03 absent direction explicit; no invented angle | Unavailable list + `?` badge | Unconfigured → reason `fixture configuration is missing`; no default north arrow | PASS |
| BL005-04 preview read-only; late responses discarded | API test + AbortController/seq | POST does not save/`updated_at`; project dump unchanged; seq + abort ignore stale | PASS |
| BL005-05 no project-schema migration or source/result mutation | Hash + live schema compare + tests | `project.schema.json` SHA `a9ededf2…` equals `HEAD:schemas/project.schema.json`; API version remains `0.7.0`; OpenAPI gained preview POST only | PASS |
| BL-001 / Stage 8 | Product grep + gated record | No satellite selector, no `map-background.mjs`; `harness/phases/2026-09-07-stage-8-bl-001-gated.md` | excluded / not implemented |
| OBS-01 | Source still uses warning text as React key | Not corrected (authorized exclusion). Duplicate-key risk retained | excluded |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git status --short --branch`; `git rev-parse HEAD`; ancestor `8751714` | dirty @ `71d4d52` | branch `codex/bl-006-ies-associations`; HEAD match; ancestor 0 | Implementation uncommitted; preserved |
| Frontend `corepack pnpm run typecheck` (from `frontend/`) | dirty @ `71d4d52` | exit 0 | `tsc --noEmit` |
| Frontend `corepack pnpm run lint` | dirty @ `71d4d52` | exit 0 | ESLint; no errors/warnings printed |
| Frontend `corepack pnpm run build` | dirty @ `71d4d52` | exit 0 | Vinext production build. Non-failing advisory: client chunk > 500 kB; some routes unclassified |
| Frontend `corepack pnpm run test` (after build) | dirty @ `71d4d52` | exit 0; **49 passed**, 0 failed | Includes new helpers + existing rendered-html suite |
| Focused backend pytest `test_fixture_direction_preview.py` + `test_phase2_catalogs.py` + `test_phase4_lighting_calculation.py` + `test_phase5_wifi_coverage.py` + `test_phase6_cap_planning.py` `-q -p no:cacheprovider --basetemp %TEMP%\lcwa-qa-*` | dirty @ `71d4d52` | exit 0 | 16+28+31+15+66 = **156** tests. Starlette/httpx deprecation warnings only |
| Full backend pytest same isolated basetemp (`backend/`) | dirty @ `71d4d52` | exit 0; **297 passed** (281 prior + 16 preview) | Same known Starlette warnings |
| Live OpenAPI vs `schemas/openapi.json` (Python compare, **no file write**) | dirty @ `71d4d52` | `openapi_equal True`; preview path present; version `0.7.0` | Write-producing `export_schema` not re-run in order to avoid mutating the dirty tree |
| `project.schema.json` `git hash-object` vs `HEAD:` | dirty @ `71d4d52` | identical `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e` | No project-schema bump |
| `scripts/validate_engineering_data.py` | dirty @ `71d4d52` | PASS | 7 catalogs; supplied-source hashes valid |
| `git diff --exit-code -- Input` | dirty @ `71d4d52` | exit 0 | Protected sources unchanged |
| `git diff --check` on product paths | dirty @ `71d4d52` | exit 0 | |
| Lockfiles / `SOFTWARE_VERSION` | dirty @ `71d4d52` | no lockfile diff; `0.7.0` | `frontend/package.json` test script only (`tests/*.test.mjs`) as authorized |
| Live MapLibre browser matrix (plan §6–12) | — | **not run** | No Playwright in `.venv` or `frontend/node_modules`; no browser MCP. Deferred honestly |

Historical implementer logs/verify files guided selection only and were not substituted for the commands above.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| QA-PR-01 | Minor | BL005-04 keyed refresh | `useEffect` depends on `[fixtureDirectionKey, project]`, so non-orientation project updates also POST preview. Sequencing/abort still drop late bodies. | Optional: depend on `fixtureDirectionKey` only. Not required to PASS BL005-04. |
| QA-PR-02 | Minor | BL006 pending control | Only the clicked checkbox is disabled (`pendingId === row.id`); other rows can fire overlapping association requests. Authoritative refresh still runs. | Optional: disable all association controls for that file while `pendingId` is set. |
| QA-PR-03 | Info | Plan browser matrix | Live production MapLibre walkthrough (three polygon tools, IES three-associate, Show coverage, CAP locate, lux vs API, card drag, rotated-map arrows) was **not** independently executed in this environment. | Scoped master may require a live pass before merge, or formally accept this deferral. |
| OBS-01 | Info (out of scope) | Duplicate React keys | Warning lists still key by warning text (`key={warning}`). Not corrected, as authorized. | Separate authorization only. |

No Critical or Major product defects confirmed. Requirements were not weakened.

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [x] Every mandatory Stages 1–7 acceptance item independently disposed as PASS or recorded as a blocking finding.
- [x] Required deterministic checks completed on the exact reviewed dirty worktree; live MapLibre matrix labeled deferred.
- [x] Source preservation, prior-phase regressions, BL-001/OBS-01/Phase 8 exclusion verified.
- [x] Verdict is supported without relying on unverified implementer claims.

## Recovery protocol

1. Preserve this QA file and dirty-tree identity `71d4d52` + uncommitted Stages 1–7 files.
2. If implementation changes, invalidate affected QA rows and retest the new exact tree.
3. Do not reset/clean/stash to “make” a clean commit without separate authorization.

## Allowed stopping conditions

- QA is complete and the supported PASS verdict is recorded. QA never authorizes the next stage, merge, or a seal.

## Verdict and next gate

- Verdict: **PASS** (item-based Independent QA for BL-003, BL-006, BL-002, BL-008, BL-007, BL-004, BL-005).
- Open findings: Minor `QA-PR-01`, `QA-PR-02`; deferred live matrix `QA-PR-03`; OBS-01 unchanged/excluded.
- Master gate eligibility: **not eligible**. Worktree is uncommitted; live MapLibre matrix is deferred; this review is not a scoped master PASS, merge authorization, or seal.
- Exact next action: scoped master decision (and any required live browser pass or commit authorization). Do **not** start BL-001. Do **not** create Phase 8 or a harness seal from this review.

## File-boundary notes (non-blocking)

Authorized per-item boundaries plus documented collateral:

- `frontend/package.json` test script glob (plan BL-003).
- `frontend/tests/rendered-html.test.mjs` (BL-006 IesAssociations; BL-008 CAP strings moved into `CapPlanningPanel`).
- `frontend/app/lib/lighting-card-position.mjs` closed-ring penultimate vertex (BL-005 work record collateral so BL-004 tests remain true).
- `schemas/openapi.json` preview endpoint (BL-005); `schemas/project.schema.json` equivalent.
- `GOALS.md` / `PLANS.md` execution-index status only.
- Harness `phases` / `logs` / `verify` dated 2026-09-07.

No satellite background, no `map-background` helper, no `harness/seals/phase-08.md`.
