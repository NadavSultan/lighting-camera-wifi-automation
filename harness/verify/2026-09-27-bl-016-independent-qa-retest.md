# Independent QA retest — 2026-09-27 — BL-016 / QA-01

Verdict: **FAIL — required Task 10 interactive coverage remains incomplete**

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: `b384bda5ad5c6e4c7175772284d0473ebe10339a` (corrective implementation `f542b164c136e8224e55867ea3f016a6987f7a44`).
- Starting status: clean tracked tree at the reviewed commit; pre-existing untracked QA files were preserved.
- Controlling contract: `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md`.
- Controlling plan: `docs/superpowers/plans/2026-09-22-bl-016-camera-pixel-density.md`, Task 10.
- Work record: `harness/phases/2026-09-22-bl-016-camera-pixel-density.md`; corrective work record: `harness/phases/2026-09-27-bl-016-qa01-cors.md`.
- Acceptance IDs: `BL016-01` through `BL016-20`.
- Reviewer/session independence: performed as a separate QA retest from the corrective evidence tip. Historical reports guided checks but were not treated as current proof.
- Review scope: exact commit, deterministic gates, fresh live verifier, browser-origin CORS, and visible production Chrome workflow.
- Non-goals: no product or acceptance edits, merge, push, later backlog work, master approval, or seal. Only this new retest report and its unique live JSON artifact were added.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Exact commit and phase scope confirmed; prior QA artifacts preserved | PASS |
| Deterministic verification | Backend/frontend suites, validator/schema freshness, source and whitespace checks | PASS |
| Acceptance-matrix review | Current deterministic and rendered evidence mapped below | FAIL overall; required Task 10 cases remain unexercised |
| Rendered/manual workflow | Production Chrome at `:3070` with API at `:8070` | PARTIAL: import, save, Camera defaults, one valid lens calculation, legend, and invalid-camera warning observed |
| Source/prior-phase regression review | Source hash/Input diff and deterministic suite evidence | PASS for deterministic/source checks; browser cross-layer workflow not completed |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| `BL016-01` lossless/idempotent migration and import | Backend suite and fresh 74-pole production UI import | Backend pytest; live JSON; Chrome showed 74 source poles | PASS |
| `BL016-02` profile defaults and validation | Backend suite; visible Camera profile | Defaults `0.5 / 2.0 / 1.25 / 50.0` in Chrome | PASS |
| `BL016-03` canonical ten-row legend | Backend suite; calculate in Chrome and inspect legend | Ten visible ranges from `2–3` through `70–∞ px/face` | PASS |
| `BL016-04` supplied-lens pinhole equation | Backend suite; visible calculation with `IMX477` and `JL-LN039 6 mm` | Current result shown; invalid second camera warned independently | PASS for one supplied lens; all-lens workflow remains unverified |
| `BL016-05` projection envelope, midpoint, CRS, distance cap | Backend suite and fresh live assertions | Deterministic suite/live JSON; project UI showed EPSG:32617 | PASS |
| `BL016-06` pinned provenance and disabled slots | Backend suite; UI surfaced unassigned enabled Camera 2 warning | Deterministic suite and visible warning | PASS |
| `BL016-07` invalid-camera isolation and warnings | Backend suite; calculate with valid Camera 1 and invalid Camera 2 | Valid-camera current result and Camera 2 missing-lens warning both visible | PASS |
| `BL016-08` canonical bands/order and determinism | Backend suite and fresh live assertions | Current backend suite/live JSON | PASS |
| `BL016-09` overlap winner/contributors | Backend suite; Task 10 map overlap inspection not completed | Backend suite only | PARTIAL |
| `BL016-10` camera/overlap/vertex/byte safety limits | Backend suite | Backend pytest | PASS |
| `BL016-11` complete fingerprint and presentation exclusions | Backend suite | Backend pytest | PASS |
| `BL016-12` stale retention/hide and replacement | Backend suite/live assertions; no completed rendered edit-save-reopen cycle | Backend suite/live JSON | PARTIAL |
| `BL016-13` atomic failed calculation | Backend suite/live controlled failure; no controlled failure through UI | Backend suite/live JSON | PARTIAL |
| `BL016-14` Camera panel, calculate action, status | Visible Chrome Camera pane and successful calculate action | Current result state observed | PASS for exercised path |
| `BL016-15` legend rendering on standard and satellite backgrounds | Standard map visible; Satellite action displayed `Satellite imagery is not configured` | Chrome observed limitation; satellite rendering unavailable | NOT VERIFIED |
| `BL016-16` overlap labels and point inspection | Not exercised in the rendered map | No current rendered evidence | NOT RUN |
| `BL016-17` edit, save/reopen, stale, failure preservation, recalculation | Initial project Save succeeded; full lifecycle not exercised | Chrome save status plus deterministic/API tests | PARTIAL |
| `BL016-18` Phase 7 report compatibility | Backend/frontend suites and fresh live verifier | Current deterministic gates/live JSON | PASS for deterministic/API scope; UI report generation not exercised |
| `BL016-19` Phase 3/prior workflows, exports, source preservation | Suites, validator, source diff/hash; visible KML import and save | Input unchanged; expected KML hash; UI did not exercise all prior workflows/exports | PASS for source/deterministic scope; rendered regressions incomplete |
| `BL016-20` complete current deterministic and production-browser evidence | Exact commit deterministic checks and visible browser-origin flow | This report, unique live JSON; Task 10 scenarios remain outstanding | FAIL |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git rev-parse HEAD`; `git status --short --branch`; `git diff --` | `b384bda5ad5c6e4c7175772284d0473ebe10339a` | Exact requested corrected tip; clean tracked start | Existing prior QA artifacts left unchanged |
| `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` from `backend/` | Same | 0 | Starlette/httpx deprecation warning |
| `..\.venv\Scripts\python.exe ..\scripts\validate_engineering_data.py` from `backend/` | Same | 0 | Eight catalogs and supplied source hashes validated |
| `..\.venv\Scripts\python.exe -m scripts.export_schema` from `backend/`; `git diff --exit-code -- schemas` | Same | 0 | Generated schemas byte-fresh |
| `corepack pnpm install --frozen-lockfile --force` (safe recovery after locked install hit access denied on existing dependency files) | Same | 0 | Local registry/cache install completed; no tracked changes |
| `corepack pnpm run build`; `corepack pnpm run test`; `corepack pnpm run typecheck`; `corepack pnpm run lint` | Same | all 0 | 107 frontend tests passed; build emitted chunk-size and dynamic-route advisories |
| `git diff --check`; `git diff --exit-code -- Input`; KML SHA-256 | Same | 0; `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328` | Supplied input unchanged |
| Fresh isolated live verifier to `harness/verify/2026-09-27-bl016-qa01-independent-retest-live.json` | Same | PASS | Its declared browser scope is shell rendering; API assertions are distinct from the manual Chrome run |
| Production Chrome `http://127.0.0.1:3070/`, isolated API `http://127.0.0.1:8070/` | Same | Import: 74 poles; Save: success | Browser KML chooser used supplied `Input/Miracle_Mile_Lighting_Poles.kml`; EPSG:32617 shown |
| Camera pane; set one isolated pole to Phoenix 1 SMART / 8 m; Camera 1 IMX477 + JL-LN039 6 mm; calculate | Same | Current result; ten-row legend; separate Camera 2 explicit-lens warning | The pole edit was staged separately from original customer data. No screenshot was retained as a file. |
| Satellite background action | Same | Alert: `Satellite imagery is not configured` | Could not validate the satellite rendered layer/colors/opacity in this environment. |

The UI run verified that the production origin can import and save over the corrected CORS path, and that a valid camera can calculate while another enabled camera has an explicit configuration warning. The full required Task 10 walkthrough was not completed: all three lenses and expected geometry, standard/satellite parity, bands transparency, two/three-camera overlaps and point inspection, stale edit/hide, save-close-reopen/recalculation, controlled failure preservation, and Phase 3–7 rendered regressions remain unverified. Current browser console/page-error counts were not captured. The live verifier's shell-only log scope is not browser-workflow evidence.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| `QA-02` | Major | Task 10 requires complete rendered workflow on the exact implementation commit for `BL016-14`–`BL016-17` and `BL016-20`. | QA-01's CORS failure is corrected: Chrome imported and saved through `:3070` to `:8070`. The manual retest established a current one-lens density result, ten-bin legend, and invalid-camera warning, but did not complete the remaining required interactive acceptance cases. Satellite imagery was also unavailable in the running app. | Complete the enumerated Task 10 browser cases with an available satellite background and capture exact UI/browser error evidence; then issue a new QA decision on the same or newer exact commit. No implementation change is implied by this evidence gap. |

## Definition of Done

- [x] Exact implementation commit and starting tree reviewed; previous evidence preserved.
- [ ] Every mandatory acceptance item independently passes or has a fully evidenced finding.
- [ ] Required rendered workflow completed on the exact reviewed commit.
- [x] Source preservation, schema freshness, source hash, and deterministic suites verified.
- [x] Verdict reflects the evidence actually gathered and does not substitute historical results for current interaction coverage.

## Recovery protocol

1. Preserved the exact requested corrected tip and all prior QA artifacts; wrote a unique live JSON output.
2. Reran the deterministic gates and verified browser-origin import/save on the corrected ports.
3. Exercised the Camera pane, one valid lens, calculated current geometry, inspected the ten-bin legend, and observed invalid-camera isolation.
4. The full interactive matrix remains incomplete; Satellite reports that imagery is not configured, so satellite parity could not be evaluated. No product files, supplied inputs, acceptance records, or seals were changed.

## Verdict and next gate

- Verdict: **FAIL — QA-02 Major remains open**.
- Master gate eligibility: **NO**.
- Exact next action: complete the remaining Task 10 rendered interactions and browser error capture in a configured live environment, then record a new independent QA decision. No merge, push, later backlog work, or seal is authorized by this review.
