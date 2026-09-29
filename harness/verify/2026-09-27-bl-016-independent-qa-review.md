# Independent QA review — 2026-09-27 — BL-016 / WA-09

Verdict: **FAIL**

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: `b237d9dceddd44005d42dab32935bda1f6eddd9d` (requested evidence tip; includes implementation commit `c6c0869aa9fe0ed2d18d70022fe37a7bf0fad170`).
- Starting status: clean (`## HEAD (no branch)`); starting diff empty.
- Controlling contract: `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md`.
- Controlling plan: `docs/superpowers/plans/2026-09-22-bl-016-camera-pixel-density.md`.
- Work record: `harness/phases/2026-09-22-bl-016-camera-pixel-density.md`.
- Acceptance IDs: `BL016-01` through `BL016-20`.
- Reviewer/session independence: independent QA performed from the specified evidence tip. Prior implementation reports and live outputs were treated as historical guidance, not independent proof.
- Review scope: implementation diff, deterministic checks, fresh isolated live verifier, and production app startup/browser inspection.
- Non-goals: no product/source edits, acceptance-status changes, merge, push, later backlog work, master self-approval, or seal.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Requested HEAD verified; clean starting tree; implementation diff and phase boundary reviewed | PASS |
| Deterministic verification | Backend suite, engineering-data validation, schema export/freshness, frontend install/tests/typecheck/lint/build, source and whitespace checks | PASS |
| Acceptance-matrix review | Each `BL016-01`–`BL016-20` independently mapped below | FAIL overall due rendered workflow finding |
| Rendered/manual workflow | Production UI opened at required isolated port 3070 | FAIL: browser API request is blocked by backend CORS configuration; downstream workflow cannot run |
| Source/prior-phase regression review | Fresh live assertions, source hash, Input diff, schema freshness; no source mutation | PASS for these deterministic/API checks; interactive prior-phase regression remains blocked by the same CORS finding |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| `BL016-01` additive, lossless, idempotent migration | Full backend suite and fresh live 74-pole import | `backend` pytest; `harness/verify/2026-09-27-bl016-qa-live.json` | PASS |
| `BL016-02` profile defaults and validation | Backend suite and live default-profile assertion | Same | PASS |
| `BL016-03` canonical Option A legend | Backend suite and live legend assertion | Same | PASS |
| `BL016-04` supplied-lens pinhole equation | Backend suite; live valid-camera bands | Same | PASS |
| `BL016-05` projection envelope, midpoint, CRS, distance cap | Backend suite | `backend` pytest | PASS |
| `BL016-06` pinned provenance and disabled slots | Backend suite | `backend` pytest | PASS |
| `BL016-07` invalid-camera isolation and warnings | Backend suite | `backend` pytest | PASS |
| `BL016-08` canonical bands/order and determinism | Backend suite | `backend` pytest | PASS |
| `BL016-09` maximum-density overlap, winner and contributors | Backend suite | `backend` pytest | PASS |
| `BL016-10` camera, overlap, vertex and byte limits | Backend suite | `backend` pytest | PASS |
| `BL016-11` complete fingerprint and presentation exclusions | Backend suite | `backend` pytest | PASS |
| `BL016-12` stale retention/hide and successful replacement | Backend suite and fresh live stale/recalculate assertions | Fresh live JSON | PASS |
| `BL016-13` atomic calculation failure | Backend suite and fresh live controlled `422` assertion | Fresh live JSON | PASS |
| `BL016-14` Camera panel, explicit calculation and status | Frontend tests/typecheck/lint pass; production UI opened, but API-backed interaction fails at startup | Frontend gates; Finding `QA-01` | FAIL |
| `BL016-15` Option A rendering on standard and satellite maps | Frontend deterministic tests pass; required interactive background workflow cannot run | Frontend tests; Finding `QA-01` | FAIL |
| `BL016-16` overlap styling and point inspection | Frontend deterministic tests pass; required interactive inspection cannot run | Frontend tests; Finding `QA-01` | FAIL |
| `BL016-17` edit, save/reopen, failure preservation and recalculation | Backend/frontend tests and API live assertions pass; full interactive persistence workflow cannot run | Fresh live JSON; Finding `QA-01` | FAIL |
| `BL016-18` Phase 7 report compatibility | Backend/frontend gates and fresh live report-package assertion | Fresh live JSON (`phase7_report: true`) | PASS |
| `BL016-19` Phase 3/prior workflows, exports and source preservation | Full backend/frontend gates, fresh live KML/report assertions, Input diff and exact KML SHA-256 | Fresh live JSON and command results below | PASS for deterministic/API scope; rendered cross-layer regressions not reached |
| `BL016-20` complete current deterministic and production-browser evidence | Deterministic gates pass; interactive production-browser acceptance is blocked by reproducible CORS defect | Finding `QA-01`; fresh live JSON explicitly limits browser evidence to shell rendering | FAIL |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git status --short --branch`; `git rev-parse HEAD`; `git diff --` | `b237d9dceddd44005d42dab32935bda1f6eddd9d` | 0 / exact HEAD, clean start | No uncommitted changes at start |
| `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` (from `backend/`) | Same | 0 | One Starlette/httpx deprecation warning |
| `..\.venv\Scripts\python.exe ..\scripts\validate_engineering_data.py` (from `backend/`) | Same | 0 | Eight catalogs and supplied-source hashes validated |
| `..\.venv\Scripts\python.exe -m scripts.export_schema` (from `backend/`) | Same | 0 | Generated schema/OpenAPI outputs |
| `git diff --exit-code -- schemas` | Same | 0 | Generated artifacts byte-fresh |
| `corepack pnpm install --frozen-lockfile` | Same | 0 | Locked install succeeded; all packages were reused from local store |
| `corepack pnpm run build` | Same | 0 | Existing large-chunk and dynamic-route classification advisories |
| `corepack pnpm run test` | Same | 0 | 107 tests passed, 0 failed |
| `corepack pnpm run typecheck` | Same | 0 |  |
| `corepack pnpm run lint` | Same | 0 |  |
| `.venv\Scripts\python.exe harness\verify\run_bl016_camera_pixel_density_live.py --output harness\verify\2026-09-27-bl016-qa-live.json` | Same | 0; `pass: true` | Unique new output; API assertions pass; headless browser scope is shell only |
| `git diff --check` | Same | 0 |  |
| `git diff --exit-code -- Input` | Same | 0 | Supplied Input unchanged |
| `Get-FileHash Input\Miracle_Mile_Lighting_Poles.kml -Algorithm SHA256` | Same | `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328` | Matches approved source hash |
| Open `http://127.0.0.1:3070/` with backend at `http://127.0.0.1:8070`; inspect initial production UI and attempt import entry | Same | UI HTTP 200; app displays `Failed to fetch` | Browser origin does not pass configured backend CORS allowlist; no interactive project workflow possible |

The production UI was visibly loaded in the browser. The requested complete workflow (all lenses, invalid camera, both backgrounds, overlap labels/inspection, persistence/reopen, controlled UI failure, and cross-layer regressions) was **not** completed. The fresh live verifier's zero console/page errors apply to its production-shell headless check only and are not rendered engineering-workflow evidence. The independent browser tool did not provide a retained screenshot artifact; the observed page showed the initial no-project state and a `Failed to fetch` toast.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| `QA-01` | Major | BL016-14–17 and BL016-20 require the interactive production workflow. The required production frontend origin is `http://127.0.0.1:3070` (plan Task 10 and fresh live runner). `backend/app/main.py` configures CORS origins only for `http://127.0.0.1:3000` and `http://localhost:3000` (lines 96–97). The browser showed `Failed to fetch` on the live UI at 3070. | The production UI at the prescribed port cannot call the API, so the 74-pole interactive flow and rendered acceptance checks are inaccessible. The separate live runner succeeds through direct API calls and renders only the application shell; it does not detect this browser integration failure. | Correct the allowed local production origin(s) within the separately authorized implementation scope, then rerun the full interactive workflow and affected deterministic/live checks on the resulting exact commit. Independent QA and master gate must review that commit. |

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [ ] Every mandatory acceptance item independently passes or has an objective finding. `BL016-14`–`BL016-17` and `BL016-20` fail due `QA-01`.
- [ ] Required rendered workflow completed on the exact reviewed commit.
- [x] Source preservation, schema freshness, Input hash, and deterministic prior-workflow/API assertions verified.
- [x] Verdict is supported without relying on unverified implementation claims.

## Recovery protocol

1. Preserved the exact implementation/evidence tip and used a new live output path; no prior evidence was overwritten.
2. The fresh verifier passed, while its own record states browser scope is shell rendering and API assertions are separate.
3. Opened the built production app against the required isolated backend/frontend ports; HTTP health and frontend shell succeeded, but the UI reported `Failed to fetch`.
4. Inspected the backend CORS configuration and confirmed the production origin on port 3070 is absent; the page remained in the no-project state, preventing later workflow actions.

This is an implementation finding, not an environmental blocker, so the QA verdict is FAIL rather than BLOCKED. Product correction is outside this review's authority.

## Verdict and next gate

- Verdict: **FAIL**.
- Open findings: `QA-01` (Major).
- Master gate eligibility: **NO**. The interactive production-browser acceptance has not passed.
- Exact next action: correct the local production CORS allowlist under separate implementation authority; then rerun the required browser workflow and affected checks on the new exact commit before a new Independent QA review. No merge, push, later backlog work, or seal is authorized by this review.
