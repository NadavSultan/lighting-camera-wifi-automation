# Independent QA review — 2026-09-29 — BL-016 final retest

Verdict: **FAIL — Major finding QA-03**

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: `b384bda5ad5c6e4c7175772284d0473ebe10339a` in `C:\Users\NadavSultan\.codex\worktrees\172c\lighting-camera-wifi-automation`.
- Starting repository state: detached at the exact requested commit, equal to `origin/codex/bl-016-qa-retest-2026-09-27`; no tracked modifications. Four pre-existing untracked QA artifacts were preserved.
- Controlling contract: `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md`.
- Controlling plan: `docs/superpowers/plans/2026-09-22-bl-016-camera-pixel-density.md`, Task 10.
- Work records: `harness/phases/2026-09-22-bl-016-camera-pixel-density.md` and `harness/phases/2026-09-27-bl-016-qa01-cors.md`.
- Acceptance IDs: `BL016-01` through `BL016-20`.
- Reviewer/session independence: a new production build and interactive Chrome retest were run at the exact implementation tip. Historical deterministic reports were treated as historical evidence only.
- Review scope: repository state, fresh production build, production browser workflows for import, camera density, stale/save/reopen/recalculation, project export, report generation, source preservation, and Satellite configuration.
- Non-goals: no product changes, acceptance-status changes, phase gate, master approval, seal, merge, or later backlog implementation.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Exact HEAD and branch tracking checked; tracked tree clean; prior evidence preserved | PASS |
| Deterministic verification | Fresh production frontend build; prior backend/frontend deterministic evidence remains historical | PARTIAL |
| Acceptance-matrix review | `BL016-01`–`BL016-20` mapped below | FAIL overall: Satellite configuration absent from built client |
| Rendered/manual workflow | Production Chrome at `http://127.0.0.1:3070/`; isolated API at `http://127.0.0.2:8070/` | PARTIAL: import, camera calculations, legend, stale lifecycle, export, and report package observed; Satellite imagery unavailable |
| Source/prior-phase regression review | Input file hash/diff and Phase 3/7 UI/export paths | PASS for checks performed; remaining prior-phase regressions follow historical deterministic evidence |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| `BL016-01` lossless migration/import | Production Chrome import of supplied KML | 74 poles loaded; EPSG:32617 displayed; prior backend suite is historical | PASS for rendered import |
| `BL016-02` defaults and validation | Camera panel inspection | Defaults `0.5 / 2.0 / 1.25 / 50.0`; invalid lower/upper envelope warning shown | PASS |
| `BL016-03` canonical ten-row legend | Calculate and inspect map legend | Ten density bands rendered | PASS |
| `BL016-04` supplied-lens projection | Calculate three supplied lens cases on a configured pole | JL-LN039 6 mm: 52°/40°, 154.7 m²; JL-LN042 3.9 mm: 69°/54°, 734.1 m²; JL-LN037 3.56 mm: 87°/68°, 57,200.9 m² | PASS for three exercised lens cases |
| `BL016-05` projection envelope, midpoint, CRS, distance cap | UI profile and result inspection | EPSG:32617 and profile limits visible; backend live assertion evidence remains in prior reports | PASS for UI and historical API evidence |
| `BL016-06` pinned provenance and disabled slots | Camera configuration UI and persisted result inspection | Result records include camera IDs and `px-face-N` method provenance | PASS for exercised result |
| `BL016-07` invalid-camera isolation and warning behavior | Valid single-camera calculation; inspect UI result | Valid calculation and legend render; invalid envelope is blocked with explicit validation | PARTIAL: UI prevents API-level invalid request |
| `BL016-08` canonical bands and determinism | Rendered density legend; inspect persisted result | Ten bands rendered; deterministic backend evidence is historical | PASS for rendering; historical deterministic coverage |
| `BL016-09` overlap winner and contributors | Configure all 74 poles with two cameras; inspect map and saved result | 147 valid footprints, 4,210 overlap pairs; 4,673 stored overlap regions with multiplicities 2–11; sample stored winner/contributor provenance. Click popup displayed winner and `px-face-10`; a 2× popup was not independently captured. | PARTIAL |
| `BL016-10` camera/overlap/vertex/byte safety limits | Historical backend suite/live verifier | Prior reports only; this retest did not exercise safety limits | Historical PASS; not rerun |
| `BL016-11` full fingerprint and presentation exclusions | Historical backend suite/live verifier | Prior reports only; this retest did not independently inspect fingerprint exclusions | Historical PASS; not rerun |
| `BL016-12` stale retention, hide, and replacement | Edit max distance, save, reopen, recalculate | Edit to 49 changed result to stale and hid density layer; save/reopen preserved stale status; valid recalc restored Current and layer | PASS |
| `BL016-13` atomic failed calculation | Attempt invalid envelope in UI | UI disabled calculation before request; no API-level failure/preservation path exercised in this retest | PARTIAL; historical API evidence only |
| `BL016-14` Camera panel, action, and status | Visible Chrome workflow | Camera pane, validation, Current/Stale states, and successful calculations observed | PASS for exercised paths |
| `BL016-15` legend on standard and satellite backgrounds | Switch background after production build | Standard map/legend rendered; Satellite action displays `Satellite imagery is not configured` | FAIL — `QA-03` |
| `BL016-16` overlap styling and point inspection | Render all-pole density map and click points | Multiplicity labels 2×–11× and overlap marks rendered; popup exposed winner, contributor, and method. Duplicate popup DOM nodes appeared after inspection; exact multi-contributor popup not captured. | PARTIAL |
| `BL016-17` edit/save/reopen/stale/failure/recalculation | UI lifecycle workflow | Stale hide, save/reopen, and successful recalc passed; API failure path was prevented by UI validation | PARTIAL |
| `BL016-18` Phase 7 report compatibility | Generate report package in production UI | UI reports `Complete with warnings`; package `fe81b6a69f3e…` | PASS for generation |
| `BL016-19` Phase 3/prior workflows, exports, and source preservation | Inspect camera geometry, project export status/API log, source hash | 147 camera footprints displayed; `Exported project JSON and updated KML`; KML export route returned 200; supplied Input unchanged | PASS for observed paths; not a complete prior-phase regression suite |
| `BL016-20` full deterministic and production browser evidence | Build plus manual acceptance workflows | Fresh frontend build succeeded; several browser paths passed, but Satellite background is unconfigured and some failure/overlap scenarios remain partial | FAIL |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git status --short --branch`; `git rev-parse HEAD`; `git remote -v`; `git branch -vv` | `b384bda5ad5c6e4c7175772284d0473ebe10339a` | 0; exact tip equals origin tracking ref | Detached checkout; four pre-existing untracked QA files preserved |
| `corepack pnpm run build` from `frontend/` with documented `NEXT_PUBLIC_API_URL` and Satellite public variables set before build | Same | 0 | Vinext emitted timing/chunk-size advisories |
| Read-only compiled bundle inspection | Same build output | Config defect reproduced | Client call compiles to `ae({})`; EOX URL absent from bundle; API URL present |
| Production Chrome `http://127.0.0.1:3070/`, isolated API `http://127.0.0.2:8070/` | Same | UI 200; API health `{"status":"ok","phase":7,"version":"0.8.0"}` | Isolated project under ignored `harness/tmp/bl016-qa03-2026-09-29/projects` |
| Import `Input/Miracle_Mile_Lighting_Poles.kml`; configure one pole; calculate JL-LN039, JL-LN042, JL-LN037 | Same | UI rendered valid current results | Three lens geometries and ten-band legend observed |
| Configure all 74 poles; two camera slots; calculate density | Same | 147 valid camera results; overlap map displayed | Saved project `ebbb7eb7-6e5f-45ea-85ac-4cb5ff18ec19`; generated data remained under ignored runtime directory |
| Change max distance to 49; save; reopen project; recalculate | Same | Stale state preserved across reopen; recalc returned to Current | Browser/API workflow |
| Set lower plane to 2.5 above upper plane 2.0 and attempt calculate | Same | Validation displayed; calculate disabled; no density API call | This does not verify the API controlled-failure atomicity case |
| Export Project; generate report package | Same | KML route HTTP 200; report status `Complete with warnings` | Report package ID prefix `fe81b6a69f3e`; download waiter timed out, but completed report status was visible after reconnect |
| Satellite background action | Same | UI displays `Satellite imagery is not configured` | Browser console error/warning capture returned empty; CUA did not expose request table or `window.performance` |
| `Get-FileHash Input\Miracle_Mile_Lighting_Poles.kml -Algorithm SHA256`; `git diff --exit-code -- Input` | Same | Hash `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`; no Input diff | Supplied source unchanged |

The build-time configuration defect is directly supported by both bundle inspection and the rendered UI state. The browser tool did not expose a Network panel/request table, so this review does not assert that EOX itself failed or that an external tile request was attempted. The application fails to configure the Satellite source before a tile request can be made.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| `QA-03` | Major | `BL016-15` requires satellite-background rendering. Public Satellite environment variables were supplied before the production build, yet the compiled client calls the configuration reader with `{}` and contains no EOX tile URL. Clicking Satellite in production Chrome shows `Satellite imagery is not configured`. | The production client bundle drops the public Satellite environment configuration, so the Satellite basemap cannot be configured or rendered. This is a reproducible product integration defect on the exact reviewed commit. | Make the approved public Satellite configuration available to the client bundle using the supported build-time/public configuration mechanism, then rebuild and independently retest satellite rendering, attribution, opacity, and density-layer parity on the new exact commit. |

## Definition of Done

- [x] Complete tracked diff and file boundary reviewed; no tracked implementation changes at the reviewed tip.
- [x] Mandatory acceptance criteria independently disposed as PASS, PARTIAL, FAIL, or historical evidence; unresolved items are explicit.
- [x] Required rendered paths were attempted on the exact reviewed commit; QA-03 is supported by current build and browser evidence.
- [x] Supplied source preservation verified; no later-phase implementation was attempted.
- [ ] All acceptance criteria pass; this is intentionally incomplete because QA-03 remains open and some UI failure/overlap cases are partial.

## Recovery protocol

1. Preserved the exact reviewed implementation tip and all prior QA artifacts.
2. Supplied the configured public environment values before a fresh production build and inspected the emitted client bundle.
3. Reproduced the missing Satellite configuration in the production UI. No application files or supplied source files were modified.
4. Completed independent camera, stale/save/reopen/recalculation, export, and report-package workflows in an isolated runtime project.

## Verdict and next gate

- Verdict: **FAIL**.
- Open findings: `QA-03` (Major).
- Master gate eligibility: **NO**.
- Exact next action: correct the client-visible Satellite configuration under implementation authority, rebuild on a new exact commit, then independently retest Satellite imagery and the remaining partial Task 10 cases. This QA result does not authorize a seal or later phase.
