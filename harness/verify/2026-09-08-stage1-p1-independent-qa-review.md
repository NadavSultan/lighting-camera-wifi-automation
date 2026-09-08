# Independent QA review — 2026-09-08 — Stage 1 P1 display reliability

Verdict: **PASS**

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: **DIRTY WORKTREE** on branch `codex/bl-006-ies-associations` at HEAD `bc45b63da41092175f7fbda97bc4c24f1f39bfe9`. There is no sealed implementation commit. Stage 1 P1 product changes are uncommitted on this SHA. Codex review baseline is this same SHA.
- Identity recorded this session:
  - `git status --short --branch`: `## codex/bl-006-ies-associations...origin/codex/bl-006-ies-associations` plus the dirty/untracked set below.
  - `git rev-parse HEAD`: `bc45b63da41092175f7fbda97bc4c24f1f39bfe9`
  - `git merge-base --is-ancestor bc45b63da41092175f7fbda97bc4c24f1f39bfe9 HEAD`: exit **0**
- Controlling contract, phase record, and acceptance IDs: `docs/web-app-review-2026-09-08.md` WA-01..WA-04; `docs/post-roadmap-backlog.md` 2026-09-08 intake + Stage 1 P1 note; `harness/phases/2026-09-08-stage1-p1-display.md`. IDs: BL-009, BL-005 follow-up, BL-010, BL-011.
- Reviewer/session independence: fresh Independent QA session. Did not implement this work. Implementer verification (`harness/verify/2026-09-08-stage1-p1-verification.md` and `harness/verify/2026-09-08-stage1-p1-live.json`) treated as claims until independently re-run/re-inspected on this dirty tree.
- Review scope: Stage 1 P1 presentation only. Live MapLibre visual confirmation of arrows/`?` and lux-label attachment was required; implementer headless arrow pixel-sample was labelled INCONCLUSIVE.
- Non-goals and excluded phases: Stage 2+ (BL-012 through BL-020); merge to `main`; Phase 8 or any harness seal; `verify_phase_readiness.py` as item gate; Input/, catalogs, lighting/Wi-Fi/CAP engines, project schema, `models.py`, lockfiles; invented azimuths or Miracle Mile CAP operational values; Phase 1–7 reacceptance.

Worktree preserved. No reset, clean, stash, revert, commit, push, or merge. Unrelated uncommitted review files preserved: `docs/web-app-review-2026-09-08.md`, `docs/post-roadmap-backlog.md`, `harness/verify/2026-09-08-web-audit-observations.json`.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | HEAD `bc45b63`; ancestor exit 0; dirty Stage 1 P1 tree preserved; no engines/schema/Input/lockfiles | PASS |
| Deterministic verification | Frontend test/typecheck/lint/build on this dirty tree; `git diff --exit-code -- Input` | PASS |
| Acceptance-matrix review | WA-01/BL-009, WA-02/BL-005 follow-up, WA-03/BL-010, WA-04/BL-011 independently disposed | PASS |
| Rendered/manual workflow | Isolated production `vinext start` and `vinext dev` MapLibre sessions with screenshots | PASS |
| Source/prior-phase regression review | Input hash unchanged; import SHA matches; no schema/engine/lockfile edits; no Phase 1–7 reacceptance claimed | PASS |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| File boundary | `git diff --name-only HEAD` vs authorized paths | Product diffs only `EngineeringMap.tsx`, `LightingPointLabels.tsx`, `LightingResultCard.tsx`, `globals.css` plus untracked scheduler/tests. Extra harness runners only. No `backend/`, `schemas/`, `Input/`, lockfiles | PASS |
| Miracle Mile 74-pole case + source SHA-256 `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` | File hash + live import `GET /api/projects/{id}` `source.file.sha256` | File and imported archive both `2f89f9f2…e328`; pole_count 74 (prod project `6c91ca85…`, dev project `9a9fd32a…`) | PASS |
| BL-009 / WA-01 viewport fit at 1920×855, 1440, 1366, 1024; collapse both rails | Live layout probe + screenshots | All four widths: `workspaceRight`/`inspectorRight`/`topbarRight` = `innerWidth`; `overflowX` false. Collapse: inspectorLeft 1878 (42 px rail). Collapse controls reachable; in-panel inspector scroll remains | PASS |
| BL-005 follow-up / WA-02 arrows after explicit SMART+azimuth; `?` for unconfigured; handle not a substitute; no invented azimuths; colours preserved | Live MapLibre after inspector SMART/azimuth 0/height 8; overlay canvas probe; screenshots | Unconfigured overlay painted (`?` path). After explicit Phoenix 1 SMART, readable SMART-blue fixture arrow plus remaining `?` badges. `.azimuth-handle` count 1 on the selected pole only. Overlay uses preview directions, not a default north arrow. `FIXTURE_ARROW_COLORS` still LITE `#ef4444` / WIFI `#facc15` / SMART `#3b82f6` | PASS |
| BL-010 / WA-03 labels stay attached after pan, zoom, fit/Locate, rotation, resize; grid not thinned | Live calculate (1638 stored points) + zoom-in screenshots + pan/rotate/resize | Zoomed map-stage: each `0.00` label sits on its calculation point. After pan and Control-drag rotate, labels remain on the point grid, not at a stale screen cluster. Resize 1920→1440: label canvas width 1324→844 and still painted. No lighting-engine or grid-spacing edit | PASS |
| BL-011 / WA-04 core stats readable without the 220 px clip; assumptions secondary; card drag does not pan the map | Live card probe + screenshots | Card max-height `min(420px, 100% - 24px)`; `statsFullyVisible` true; body clientHeight = scrollHeight 113; Eavg/Emin/Emax/Emin/Eavg/Emin/Emax all present. Assumptions in collapsed `<details>`. Header drag left overlay paint size unchanged | PASS |
| Stage 2+ / merge / Phase 8 / engines | Diff + source inspection | Not implemented. No seal. CAP test inputs used only as test-only and did not complete Recommend in this session | excluded |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git status --short --branch`; `git rev-parse HEAD`; `git merge-base --is-ancestor bc45b63da41092175f7fbda97bc4c24f1f39bfe9 HEAD` | dirty @ `bc45b63` | branch match; HEAD match; ancestor 0 | Implementation uncommitted; preserved |
| `git diff --exit-code -- Input` | dirty @ `bc45b63` | exit 0 | Protected sources unchanged |
| Independent file SHA-256 of `Input/Miracle_Mile_Lighting_Poles.kml` | dirty @ `bc45b63` | `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` | Matches required source identity |
| Frontend `corepack pnpm run typecheck` (from `frontend/`) | dirty @ `bc45b63` | exit 0 | `tsc --noEmit` |
| Frontend `corepack pnpm run lint` | dirty @ `bc45b63` | exit 0 | ESLint; no errors/warnings printed |
| Frontend `corepack pnpm run build` | dirty @ `bc45b63` | exit 0 | Vinext production build. Non-failing advisories: client chunk > 500 kB; some routes unclassified; plugin-timings |
| Frontend `corepack pnpm run test` (after that build) | dirty @ `bc45b63` | exit 0; **70 passed**, 0 failed | Includes `map-frame-scheduler.test.mjs` and `workspace-layout.test.mjs` plus rendered-html SSR |
| `git diff --check` on product paths | dirty @ `bc45b63` | exit 0 | |
| Live import SHA after KML open | isolated `LCWA_DATA_DIR` `harness/tmp/stage1-p1-qa` | `source.file.sha256` equals expected; 74 poles | Production and later dev imports |
| Live production `vinext start` on 3078, API 8078, `NEXT_PUBLIC_API_URL` rebuild | dirty @ `bc45b63` | layout/card/arrows/labels visually confirmed | Ports 3000/8000 were occupied; isolated ports used. Screenshots under `harness/tmp/stage1-p1-qa/screenshots/prod-*.png`. JSON `harness/verify/2026-09-08-stage1-p1-independent-qa-live.json` |
| Live development `vinext dev` on 3078, API 8078 | dirty @ `bc45b63` | hash_ok/card_ok/arrows_painted/labels_painted true | `wait_until=load` (networkidle hung on the Vite websocket). JSON `harness/verify/2026-09-08-stage1-p1-independent-qa-dev.json` |

Historical implementer logs/verify files guided selection only and were not substituted for the commands above.

Scheduler unit tests prove cancel-without-null is fixed. That was **not** accepted as a substitute for live arrows/labels. Live MapLibre screenshots were inspected.

Playwright was used from the local `.venv` for this QA run only. It is not a product dependency and is not in the lockfile.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| QA-S1-01 | Info | BL-010 CAP “Show selected sites on map” | Test-only CAP candidate row never exposed **Mark test-only feasible** after **Add selected pole as CAP site**, so Recommend / Show selected was not executed. Pan, zoom-in, Control-drag rotate, and resize **did** keep labels on their points. This is a QA-script gap for that one map action, not an observed detached-label miss. | Optional before merge: one live CAP easeTo with test-only inputs (not site-design values). Not required to reverse this PASS given the other motion evidence. |
| QA-S1-02 | Info | Implementer residual: headless `getImageData` empty | Independent copy-canvas sampling on production returned non-zero painted pixels for both arrow and label overlays. Visual screenshots confirmed SMART arrow, `?` badges, and attached `0.00` labels. Implementer INCONCLUSIVE pixel-sample is superseded for this tree. | None. |
| QA-S1-03 | Info | BL-011 live lighting values | Calculated area had no eligible IES, so Eavg/Emin/Emax are `0.00 lx` and ratios `—`, with 1638 zero points. Core stats were still unclipped. This is not BL-017 and is not a calculation-engine change. | None for Stage 1 P1. |
| QA-S1-04 | Info | WIFI yellow live arrow | LITE red poles and one SMART blue arrow were live. A dedicated WIFI-yellow arrow was not configured in this session. Colour constants were unchanged in source. | Optional colour-spot check. Not blocking. |
| QA-S1-05 | Info | Dirty worktree | No implementation commit exists. Playwright and Vinext isolated rebuild artifacts remain local. | Commit only under separate authorization. |

No Critical or Major product defects confirmed. Requirements were not weakened. Stage 2+ was not entered.

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [x] Every mandatory Stage 1 P1 acceptance item independently disposed as PASS or recorded as a blocking finding.
- [x] Required deterministic and rendered checks completed on the exact reviewed dirty worktree.
- [x] Source preservation, later-stage exclusion, and no Phase 1–7 reacceptance verified.
- [x] Verdict is supported without relying on unverified implementer claims.

## Recovery protocol

1. Preserve this QA file, `harness/verify/2026-09-08-stage1-p1-independent-qa-live.json`, `harness/verify/2026-09-08-stage1-p1-independent-qa-dev.json`, and dirty-tree identity `bc45b63` plus uncommitted Stage 1 P1 files.
2. Record: production live completed; first dev `networkidle` goto timed out; second dedicated `vinext dev` session with `wait_until=load` succeeded. Worktree was not reset.
3. If implementation changes, invalidate affected QA rows and retest the new exact tree.
4. Do not reset/clean/stash to invent a clean commit without separate authorization.

## Allowed stopping conditions

- QA is complete and the supported PASS verdict is recorded. QA never authorizes the next stage, merge, commit, or a seal.

## Verdict and next gate

- Verdict: **PASS** (item-based Independent QA for BL-009, BL-005 follow-up, BL-010, BL-011 on dirty HEAD `bc45b63da41092175f7fbda97bc4c24f1f39bfe9`).
- Open findings: Info `QA-S1-01`–`QA-S1-05` only.
- Master gate eligibility: **this review makes a later scoped master decision eligible**. It does **not** itself authorize merge, commit, or Stage 2. The worktree is still uncommitted. No Phase 8. No seal.
- Exact next action: scoped master decision on this dirty identity (or on a later authorized commit of the same product files). Do **not** start Stage 2. Do **not** merge to `main` from this review.

## File-boundary notes (non-blocking)

Authorized product paths changed or added:

- `frontend/app/globals.css`
- `frontend/app/components/EngineeringMap.tsx`
- `frontend/app/components/LightingPointLabels.tsx`
- `frontend/app/components/LightingResultCard.tsx`
- `frontend/app/lib/map-frame-scheduler.mjs`
- `frontend/app/lib/map-frame-scheduler.d.mts`
- `frontend/tests/map-frame-scheduler.test.mjs`
- `frontend/tests/workspace-layout.test.mjs`

Harness/backlog collateral (not product engines): implementer `harness/verify/run_stage1_p1_live.py` plus this QA’s `harness/verify/run_stage1_p1_independent_qa_live.py` and JSON/review records. `docs/post-roadmap-backlog.md` Stage 1 P1 status note remains the preserved intake document.

## Live environment (this QA)

- API `http://127.0.0.1:8078`, UI `http://127.0.0.1:3078`, `LCWA_DATA_DIR` / `LCWA_CATALOG_DIR` under `harness/tmp/stage1-p1-qa`.
- Health: `{"status":"ok","phase":7,"version":"0.7.0"}`.
- CAP values, where attempted, were test-only and are not approved Miracle Mile site-design values.
