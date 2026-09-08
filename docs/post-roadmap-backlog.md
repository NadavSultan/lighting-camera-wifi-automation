# Post-roadmap backlog

Established: 2026-09-06. Authority: user's post-roadmap master-session instruction, limited to intake, clarification, classification, and backlog maintenance. Implementation requires separate authorization for a specific item. No Phase 8 is created or authorized.

## Current live-review intake — 2026-09-08

The latest exploratory review is [the English web-app review](web-app-review-2026-09-08.md), supported by [measured observations](../harness/verify/2026-09-08-web-audit-observations.json). It reviewed clean branch `codex/bl-006-ies-associations` at `bc45b63da41092175f7fbda97bc4c24f1f39bfe9`, not the historical main baseline below. No product changes or acceptance decisions were made. The review sections are the controlling intake details for the following independently scoped follow-ups, including reproduction, expected behavior, subsystem, severity/priority, risks/dependencies, acceptance, verification and contract impact.

| Backlog ID | Review section | Type / state | Recommended route |
|---|---|---|---|
| BL-009 | WA-01: right inspector / workspace clipping | Bug, reproduced; P1 | Small corrective task |
| BL-005 follow-up | WA-02: missing direction arrows / unavailable badges | Bug, reproduced; P1; original improvement now needs diagnosis | Diagnose canvas lifecycle, then correction |
| BL-010 | WA-03: lux labels detached from map points | Bug, reproduced; P1; follow-up to BL-007 | Diagnosis then correction |
| BL-011 | WA-04: lighting card hides core statistics | Usability bug, reproduced; P1; follow-up to BL-004 | Small corrective task |
| BL-012 | WA-05: lighting card anchor offset | Bug, observed with supporting code evidence; P2 | Small corrective task after layout |
| BL-013 | WA-06: revisit results across multiple areas | Improvement; P2; disappearance on polygon creation not conclusively reproduced | Scoped UI task; diagnose exact disappearance separately |
| BL-014 | WA-07: result-first CAP workflow | Improvement; P2; follow-up to BL-008 | Dedicated UI contract preserving Phase 6 prerequisites |
| BL-015 | WA-08: explain camera projection boundary | Improvement; P2 | Small explanatory UI task |
| BL-016 | WA-09: camera pixel-density heatmap | Feature; P3 | Dedicated engineering contract, separate authorization |
| BL-017 | WA-10: distinguish tiny lux from exact zero | Improvement; P2 | Small numeric-presentation task |
| BL-018 | WA-11: organize left workflow panel | Improvement; P2 | Scoped UI design/task |
| BL-019 | WA-12: stale phase/gating UI messages | Content bug; P3 | Small corrective task |
| BL-020 | WA-13: duplicate React warning keys | Technical bug observed in dev-server log; P3 | Small corrective task preserving warnings |

All items remain **recorded, not authorized for implementation by this review**. No Phase 8 is created. Existing BL-001–008 intake and subsequent scoped decisions remain historical context; the live observations above do not rewrite accepted Phase 1–7 contracts.

## Cursor handoff readiness

This backlog and the linked English review are ready for intake and diagnosis, not blanket implementation. See the review's **Cursor handoff readiness** section for the required item-specific authorization, reproduction, execution plan, file boundary and verification. The older 2026-09-06 plan does not automatically cover this new review round. UI redesign items need a settled scope; BL-016 needs a dedicated engineering contract.

## Stage 1 P1 implementation — 2026-09-08

User authorized Stage 0 + Stage 1 only (BL-009, BL-005 follow-up, BL-010, BL-011) via the Codex-staged plan. Work record: `harness/phases/2026-09-08-stage1-p1-display.md`. Independent QA PASS: `../harness/verify/2026-09-08-stage1-p1-independent-qa-review.md`. Scoped master CONDITIONAL PASS: `post-roadmap-stage1-p1-scoped-master-decision-2026-09-08.md` (dirty HEAD `bc45b63`; commit authorized; merge and Stage 2+ not authorized).

| ID | Implementation status |
|---|---|
| BL-009 | CONDITIONAL PASS; live viewport fit at 1920/1440/1366/1024 |
| BL-005 follow-up | CONDITIONAL PASS; rAF leak proven; live SMART arrow and unconfigured `?` |
| BL-010 | CONDITIONAL PASS; labels stayed attached through pan/zoom/rotate/resize; grid not thinned |
| BL-011 | CONDITIONAL PASS; core stats unclipped; assumptions collapsed; card max-height no longer 220px |

## Stage 2 implementation — 2026-09-08

User authorized Stage 2 items BL-012, BL-017, and BL-018 only via `docs/superpowers/plans/2026-09-08-stage2-bl-012-017-018.md`. Work record: `harness/phases/2026-09-08-stage2-bl-012-017-018.md`. Implementer verification: `../harness/verify/2026-09-08-stage2-bl-012-017-018-verification.md`. Independent QA and merge remain unauthorized. Stage 3+ remain gated.

| ID | Implementation status |
|---|---|
| BL-012 | Implementer PASS; live card ~12 px from finish vertex with map origin not at (0,0) |
| BL-017 | Implementer PASS; exact 0 → `0.00 lx`, null → `—`, tiny positive → `<0.01 lx` |
| BL-018 | Implementer PASS; Lighting/Camera/Wi-Fi/CAP switcher; overflowX false at 1920/1024 |

## Baseline and accepted gates

Startup review used clean `main` at `8751714003bf09f39c217a5f26b9fd6056d2927b`, equal to freshly fetched `origin/main`. Working checkout: `C:/Users/NadavSultan/Desktop/Nadav/lighting-camera-wifi-automation/lighting-camera-wifi-automation`. The parent checkout contains unrelated uncommitted work and was preserved unchanged.

The ten startup documents and Phase 1–7 closure records were read. Closure evidence is historical; this intake session did not rerun product verification or issue acceptance decisions.

- Phase 1: [completion report](phase-1-completion-report.md), with accepted/frozen status in [implementation plan](implementation-plan.md).
- Phase 2: [final independent retest](phase-2-nir-01-final-retest-report.md).
- Phase 3: [final focused retest](phase-3-final-focused-retest-report.md).
- Phase 4: [master gate](phase-4-master-gate-decision-2026-08-26.md).
- Phase 5: [master gate](phase-5-master-gate-decision-2026-08-27.md).
- Phase 6: [master gate](phase-6-master-gate-decision-2026-09-03.md) and [seal](../harness/seals/phase-06.md).
- Phase 7: [master gate](phase-7-master-gate-decision-2026-09-05.md) and [seal](../harness/seals/phase-07.md).

Accepted limitations are not automatically bugs. Preserve source bytes, customer poles, separate source/edit/calculation/recommendation layers, accepted behavior, and existing gates. A backlog entry cannot amend a contract or authorize execution.

## Item register

Eight user requests received on 2026-09-06. Initial triage used user reports, source inspection, and accepted records at `8751714`. A subsequent authorized live walkthrough reproduced BL-002/003/006/008; see the dated updates below and the linked evidence. No implementation was performed. Priorities below are provisional recommendations, not user-approved scheduling. All implementation remains unauthorized.

| ID | Title | Type | Severity | Priority | Status | Recommended route | Implementation authorization |
|---|---|---|---|---|---|---|---|
| BL-001 | Satellite background option | feature | N/A | P2 | Implemented 2026-09-07 (awaiting independent QA; not accepted) | Dedicated implementation contract | Authorized 2026-09-07 — see [provider authorization](post-roadmap-bl-001-provider-authorization-2026-09-07.md); verification `../harness/verify/2026-09-07-bl-001-verification.md` |
| BL-002 | Make conceptual Wi-Fi visible and discoverable | improvement | Medium | P1 | Live usability issue confirmed | Small corrective task; contract decision if auto-enabled | Not authorized |
| BL-003 | Visible polygon drawing progress | bug | Medium | P1 | Early-vertex feedback defect reproduced | Small corrective task | Not authorized |
| BL-004 | Movable lighting results window | feature | N/A | P2 | Triaged | Dedicated implementation contract | Not authorized |
| BL-005 | Direction arrow at every fixture | improvement | Medium | P2 | Triaged | Dedicated implementation contract | Not authorized |
| BL-006 | Clear multi-type IES assignment | improvement | Medium | P1 | Three associations verified live; UI ambiguity confirmed | Small corrective task | Not authorized |
| BL-007 | Numerical illuminance at calculation points | improvement | Medium | P2 | Triaged | Small corrective task | Not authorized |
| BL-008 | Discoverable CAP recommendation workflow | improvement | Medium | P1 | Recommendation executed; usability issue confirmed | Dedicated implementation contract | Not authorized |

## BL-001 — Satellite background option

- **Request/objective:** User wants satellite imagery as an alternative to the standard map.
- **Type:** Feature: adds a background source and selection capability.
- **Current behavior/evidence:** `frontend/app/components/EngineeringMap.tsx`, `BASE_STYLE`, configures only OpenStreetMap raster tiles. No satellite selector was found in the map/workspace. This is source-confirmed, not browser-reproduced.
- **Reproduction:** Open a project and inspect background controls; currently only the standard background is configured.
- **Expected behavior:** An explicit Standard/Satellite choice changes the background while keeping the engineering workspace usable.
- **Subsystem:** Map background, attribution, provider configuration, optional UI preference storage.
- **Severity/priority:** N/A (new capability); P2, improves site interpretation without evidence that current workflows are blocked.
- **Dependencies:** Imagery provider, terms, attribution, and persistence were open at intake. **Resolved 2026-09-07:** free EOX public WMTS with attribution; session-only choice; environment config; provider must remain replaceable (not saved in project JSON). See [provider authorization](post-roadmap-bl-001-provider-authorization-2026-09-07.md). BL-002/003/005/007 must remain legible over imagery.
- **Risks:** Tile availability, credential exposure, imagery age/alignment, extra network use, and accidentally resetting overlays on background change.
- **Acceptance criteria:** Both backgrounds are selectable; switching retains viewport, selection, drawings, results, and layer state; required attribution remains visible; unavailable imagery produces a readable state and allows return to Standard; source bytes and coordinates remain unchanged.
- **Verification:** Browser checks for repeated switching with all engineering overlays and an active draft, failed tile requests, attribution, and supported zoom ranges; frontend tests/typecheck/lint/build; persistence/migration tests only if persistence is added.
- **Contract impact:** Additive change to Phase 1 map/architecture behavior; no calculation change. Storage changes would require an explicit compatibility decision. Existing accepted records are not amended here.
- **Route/open decisions:** Dedicated implementation contract. **Closed 2026-09-07:** session-only; Standard = current OSM; Satellite = environment-configured tiles, first backend = free EOX public WMTS; may replace the satellite provider later without a project-schema change. XYZ/attribution verified at implementation 2026-09-07. Product implemented; independent QA and scoped master decision still required (`../harness/verify/2026-09-07-bl-001-verification.md`).

## BL-002 — Make conceptual Wi-Fi visible and discoverable

**Live update — 2026-09-06:** Calculation produced one 30 m conceptual circle but left the layer off. Explicitly enabling Conceptual Wi-Fi displayed the circle. Usability issue confirmed; no rendering failure reproduced in this case. Recommend a small presentation/guidance task; automatic display requires a contract decision. See [live reproduction evidence](../harness/verify/2026-09-06-backlog-live-reproduction.md). The following initial-triage details are retained as history where superseded.

- **Request/objective:** User needs to see coverage on the map; side-panel area statistics are secondary.
- **Type:** Usability improvement provisionally; classify a reproduced failure to draw valid enabled coverage as a bug.
- **Current behavior/evidence:** `EngineeringMap.tsx` builds circles from `wifi_coverage.result.circles` and renders cyan fill at opacity 0.16 only when the result exists and `layer_state.wifi_coverage` is true. The workspace exposes Calculate conceptual Wi-Fi and a Conceptual Wi-Fi layer toggle. The accepted Phase 5 contract map additions explicitly keeps this layer off until an explicit toggle. User reports insufficient visibility; the exact runtime state is unknown.
- **Reproduction to perform:** Configure an eligible active WIFI/SMART fixture, calculate Wi-Fi, compare the map before/after enabling Conceptual Wi-Fi; repeat with no analysis polygon, then with one. Record result count, toggle state, zoom, screenshot, and browser errors if absent.
- **Expected behavior:** A clearly discoverable coverage display shows current conceptual circles and their extents; statistics remain available with less prominence. Actual on-map geometry is requested, not a verified RF prediction.
- **Subsystem:** Wi-Fi map rendering, layer control, calculation feedback, sidebar information hierarchy.
- **Severity/priority:** Medium/P1: obstructs visual assessment of an existing capability.
- **Dependencies/risks:** Valid eligible inputs/results; distinguish low contrast, layer-off state, stale results, and rendering faults. Preserve radius semantics, 500-circle limits, layer persistence, disclaimers, and accepted statistics. Satellite contrast relates to BL-001 but is not a prerequisite.
- **Acceptance criteria:** With current results and coverage enabled, every eligible circle is visible at its stored location/radius even without an analysis area; overlapping circles and fixture markers remain distinguishable; absent/stale/zero results have clear explanations; users can readily find how to show/hide coverage; statistics remain accessible.
- **Verification:** Production browser workflow on the supplied 74-pole source plus no-area, zero-circle, disabled/ineligible fixture, stale-result, toggle, and save/reopen cases; compare geometry to stored result rings; Phase 5 regression and source-preservation checks if behavior changes.
- **Contract impact:** No engine change intended. Automatically enabling coverage after calculation would change the explicit Phase 5 default/toggle rule and needs an approved amendment; merely improving visibility and guidance does not. Do not silently remove required statistics.
- **Route/open decisions:** Diagnosis first, then a bounded corrective task if needed. Determine whether explicit show-coverage guidance suffices or the user wants automatic display.

## BL-003 — Visible polygon drawing progress

**Live update — 2026-09-06:** Reclassified as **bug**: first and second lighting-polygon clicks incremented the vertex count without any visible point/segment; a faint fill appeared at the third click. Controls/guidance were below the visible sidebar. Recommend a small corrective task. Other polygon tools still require live verification before a fix is considered complete. See [live reproduction evidence](../harness/verify/2026-09-06-backlog-live-reproduction.md). The following initial-triage details are retained as history where superseded.

- **Request/objective:** Thicker outline, clear current drawing position, marked area, and next step.
- **Type:** Usability improvement with a suspected early-draft rendering defect, not yet reproduced live.
- **Current behavior/evidence:** `EngineeringMap.tsx` `draftFeature` emits no geometry for one point, a LineString for two, and a closed Polygon from three. All three draft sources have fill layers but no dedicated line/vertex layers. This suggests missing visual feedback for the first two vertices. Workspace guidance is mostly in the sidebar; no live cursor-to-last-vertex preview was found.
- **Reproduction:** Start each of lighting, camera-priority, and Wi-Fi polygon drawing; inspect zero/one/two/three vertices, cursor movement, closure, and cancellation. Repeat redraw of a saved polygon.
- **Expected behavior:** A high-contrast thick outline, visible placed vertices/current cursor position, marked-area preview, and concise next-step guidance throughout drawing. “Current position” means drawing cursor, not device geolocation.
- **Subsystem:** Shared map draft rendering and polygon interaction guidance.
- **Severity/priority:** Medium/P1: users struggle to complete a core geometry-input operation.
- **Dependencies/risks:** Coordinate preview must remain transient; preserve distinct polygon collections, validity checks, prior saved geometry during redraw, and fixture selection/pan behavior. Visual preview must not imply a draft is already saved.
- **Acceptance criteria:** First vertex is visible; second creates a visible segment; further vertices show a clear area preview; current segment and committed draft edges are distinguishable; guidance identifies add/finish/cancel actions; invalid completion explains the problem without replacing saved geometry; all three polygon tools behave consistently.
- **Verification:** Browser checks at several zooms over light/dark backgrounds, each vertex stage, cancel, invalid/self-intersecting polygon, redraw, and save/reopen; relevant geometry-validation regressions and frontend checks. Verify preview does not alter stored coordinates.
- **Contract impact:** Additive UI behavior across Phases 3–5, preserving accepted draft/validation contracts; no geometry algorithm change requested.
- **Route/open decisions:** Focused diagnosis of early-vertex visibility, then a small corrective task if confined to presentation. Agree final outline/vertex styling before implementation.

## BL-004 — Movable lighting results window

- **Request/objective:** Clicking Calculate Lighting opens a compact movable window beside the polygon at the place drawing finished, containing average illuminance and uniformity.
- **Type:** Feature: introduces an anchored, draggable results-window interaction.
- **Current behavior/evidence:** `EngineeringWorkspace.tsx` `calculateSelectedArea` updates the project/status; calculation-area rows show Eavg, Emin, Emax, Emin/Eavg and Emin/Emax in the sidebar. No draggable on-map result window was found.
- **Reproduction:** Draw/save/select a calculation area and click Calculate Lighting; inspect where the resulting statistics appear.
- **Expected behavior:** On successful calculation, show that area's current results beside its last drawing position and allow dragging anywhere within the map.
- **Subsystem:** Lighting results presentation, map overlay interaction, area selection and transient UI state.
- **Severity/priority:** N/A (new interaction); P2, existing sidebar results remain available.
- **Dependencies/risks:** Define anchor for reopened areas without drawing history, edge-of-screen placement, map pan/zoom behavior, multiple windows, and position persistence. Avoid stale or wrong-area values, obstructed drawing, and rounding that changes authoritative results. BL-003 is related but not required.
- **Acceptance criteria:** Successful calculation opens the correct named area window near its drawing endpoint; window shows average illuminance in lx and explicitly named Emin/Eavg and Emin/Emax ratios; dragging does not pan the map or change geometry; window remains recoverable at map edges; loading/failure is clear; invalidated/deleted area results cannot remain displayed as current; accepted limitations remain accessible.
- **Verification:** Browser calculate/drag/pan/zoom/resize, multiple-area selection, recalculate, failed calculation, undo/redo, stale result, delete and reopen cases; compare displayed statistics to returned results, including null/zero ratios; frontend checks and affected lighting regressions.
- **Contract impact:** Extends Phase 4 result presentation, with no equation or uniformity-definition change. Any persisted window/anchor fields need a separate schema/migration decision; Phase 7 exports remain unchanged.
- **Route/open decisions:** Dedicated implementation contract for window lifecycle, anchor fallback, and persistence. These choices remain open.

## BL-005 — Direction arrow at every fixture

- **Request/objective:** Show an arrow beside each fixture indicating the lighting fixture azimuth.
- **Type:** Usability improvement: exposes existing orientation values across the map.
- **Current behavior/evidence:** Fixture map features contain identity/type/activity but no azimuth. `EngineeringMap.tsx` creates an azimuth drag marker only for a selected configured SMART fixture; it does not render arrows for all fixtures.
- **Reproduction:** Configure differently oriented LITE/WIFI/SMART fixtures and inspect the map with and without a selected fixture.
- **Expected behavior:** Every fixture with an authoritative lighting orientation has a clear direction arrow; missing configuration is explicitly distinguishable rather than assigned an invented direction.
- **Subsystem:** Fixture map symbols, effective configuration, bearing display.
- **Severity/priority:** Medium/P2: orientation is difficult to inspect across a layout.
- **Dependencies/risks:** Apply the existing fixture azimuth convention, not either camera-slot offset; account for map rotation and projected/grid versus display-north conventions without inventing a new one. Dense layouts, inactive/unconfigured fixtures, marker colors, and overlap need explicit presentation rules. Do not add new rotation controls implicitly.
- **Acceptance criteria:** Arrows represent stored effective fixture azimuths for LITE/WIFI/SMART without requiring selection; directions remain correct on map rotation/zoom and after edits/undo/reopen; unconfigured cases are clear; customer coordinates and fixture colors remain unchanged; arrows do not block selection or imply IES beam extent.
- **Verification:** Cardinal and near-north azimuth cases, different camera offsets, rotated map, dense 74-pole layout, inactive/unconfigured fixtures, azimuth edits and save/reopen; compare with accepted orientation conventions and current calculations; frontend and affected orientation regressions.
- **Contract impact:** Additive Phases 2–4 display behavior; no new editing authority, photometric convention, or camera geometry change. Any change to azimuth conventions requires separate review.
- **Route/open decisions:** Dedicated implementation contract for per-fixture eligibility, map bearing, arrow sizing and visibility rules.

## BL-006 — Clear multi-type IES assignment

**Live update — 2026-09-06:** One Phoenix 100 W IES retained three active LITE/WIFI/SMART associations, confirmed by API and a freshly reopened catalog. No one-type restriction was reproduced. Recommend a small UI task to show and manage all current associations. A different file-specific failure remains possible; exact file/model/error details would be needed to diagnose that case. See [live reproduction evidence](../harness/verify/2026-09-06-backlog-live-reproduction.md). The following initial-triage details are retained as history where superseded.

- **Request/objective:** Each individual IES file must be assignable to LITE, WIFI, and SMART; user reports only one group/type is possible.
- **Type:** Usability improvement provisionally, with a possible association bug pending reproduction. Source evidence does not show a one-type-only data restriction.
- **Current behavior/evidence:** `CatalogManager.tsx` has a single file/model pair selector and an Associate action; it does not summarize all associations per file. `CatalogStore.associate_ies` appends or updates an association keyed by the file/model pair, preserving other pairs. `docs/decision-log.md` DL-011 compatibility decision restricts supplied Phoenix files to Phoenix 1 LITE/WIFI/SMART and Solitaire files to Solitaire LITE/WIFI/SMART, by source hash. This is a family restriction, not a one-type limit.
- **Reproduction:** Upload one valid IES, associate it to a compatible LITE model, then compatible WIFI and SMART models; reload catalog and inspect all three associations and per-pole selection. Capture exact file/hash, model IDs, errors, and whether earlier associations disappear. Repeat separately with a supplied family-restricted file.
- **Expected behavior:** One file can hold explicit simultaneous associations with all three compatible fixture types, and its current assignments are obvious and independently editable.
- **Subsystem:** IES catalog association UI, catalog persistence, fixture selection and compatibility validation.
- **Severity/priority:** Medium/P1 provisionally: reported obstacle to assigning lighting data; escalate if valid associations are lost or blocked.
- **Dependencies/risks:** Fixture type and model family must remain distinct. Preserve valid/active-file requirements, source bytes/hash, immutable revisions, explicit pole pins, and independent default selection. Do not bypass supplied-family restrictions or auto-associate every upload.
- **Acceptance criteria:** A single valid file can be explicitly associated with compatible LITE/WIFI/SMART models at once; all associations are visible after refresh/reopen; removing one leaves the others; each compatible pole can select the same file; invalid/inactive files and prohibited cross-family assignments retain readable rejection; defaults and existing pins remain unchanged unless explicitly changed.
- **Verification:** UI and API sequence for adding three/removing one, repeated association, catalog reload, pole assignment/save/reopen, revision pins, invalid files, and both supplied-family restrictions; Phase 2 catalog/API and Phase 4 compatibility regressions; byte/hash preservation.
- **Contract impact:** No change for multi-type assignments within compatible families: this restores/exposes accepted many-to-many behavior. “Every file across every model family” would conflict with the approved supplied-file mapping and requires explicit engineering authority; it is not assumed here.
- **Route/open decisions:** Diagnosis first. If persistence works, a small corrective UI task; if a restriction fails incorrectly, a bounded bug fix. Clarify whether the request includes cross-family use only if that proves relevant.

## BL-007 — Numerical illuminance at calculation points

- **Request/objective:** Each lighting calculation point must show its numerical illuminance as well as color.
- **Type:** Usability improvement: numerical results already exist, but the map omits labels.
- **Current behavior/evidence:** `EngineeringMap.tsx` `calculationPointFeatures` includes maintained horizontal illuminance in `lux`; the map renders two circle layers with color/size and no numerical text layer.
- **Reproduction:** Calculate a valid lighting area and inspect points at a readable zoom; current map styling supplies colors without values.
- **Expected behavior:** Each point has a directly visible numerical maintained-illuminance value with an unambiguous lx unit convention; hover alone is insufficient for this request.
- **Subsystem:** Lighting point map presentation and numerical formatting.
- **Severity/priority:** Medium/P2: users cannot read individual results from the map.
- **Dependencies/risks:** Choose display precision and text rendering/font availability; address dense grids, overlap, zoom and performance without silently omitting required values. Preserve authoritative precision, color semantics and stale-result invalidation. Related to BL-001/004 but independently scoped.
- **Acceptance criteria:** Every displayed calculation point has its corresponding numeric value alongside color; units and rounding are clear; zero is shown as zero, not missing; labels use stored maintained lux and never recalculate; values remain readable at working zoom; stale/deleted results disappear; overlapping areas can be distinguished. Any zoom-based suppression requires explicit agreement rather than weakening the request.
- **Verification:** Compare every label in a small known dataset against results; cover zero, low/high/fractional values, dense supported grids, overlapping areas, map zoom/rotation, stale results, and reopen; visual contrast/performance checks and frontend test/typecheck/lint/build. Lighting-engine tests are required only if engine paths are affected.
- **Contract impact:** Additive Phase 4 display requirement, with no change to illuminance equations or saved/exported precision; no Phase 7 export change requested.
- **Route/open decisions:** Small corrective task after defining precision and dense-grid presentation. If new external font/service dependencies or persistence are proposed, expand the work contract before execution.

## BL-008 — Discoverable CAP recommendation workflow

**Live update — 2026-09-06:** Recommend CAP executed with test-only profile/candidate data and selected the one available site. Count and topology are below the long form; map layers remained off until explicitly enabled. Keep as a usability improvement requiring a focused workflow contract. Separate development-console observation OBS-01 is recorded in the evidence report and is not bundled into this implementation scope. See [live reproduction evidence](../harness/verify/2026-09-06-backlog-live-reproduction.md). The following initial-triage details are retained as history where superseded.

- **Request/objective:** Make it clear where to obtain the recommended CAP count and locations, and how to interpret the result.
- **Type:** Usability improvement; recommendation exists, so this is not presently classified as a missing-engine bug.
- **Current behavior/evidence:** `EngineeringWorkspace.tsx` includes toolbar Recommend CAP, a CAP sidebar with operation mode/permission, input blockers, explicit candidates, Calculate / rank, Validate, Recommend, a selected count, and collapsed topology/provenance. `phase6-cap-workflows.mjs` disables actions for missing prerequisites or mismatched mode. Map CAP layers exist. User reports difficulty locating and understanding this workflow; no live task-observation was performed.
- **Reproduction:** Open a fresh imported project, locate recommendation controls, inspect disabled states and their explanations; then use an approved test profile/candidate pool to recommend and locate count/sites on the map. Do not mark real sites feasible merely to enable a button.
- **Expected behavior:** A discoverable CAP entry explains prerequisites and the next action; clearly distinguishes ranking, validation and recommendation; presents the recommended count and selected locations together with exclusions, unresolved nodes and limitations.
- **Subsystem:** CAP workflow navigation, prerequisite explanations, recommendation summary and map/list selection.
- **Severity/priority:** Medium/P1: a core accepted workflow is difficult to use even though controls exist.
- **Dependencies/risks:** Preserve approval-bearing inputs, unknown blockers, approved candidate pool, permissions, locks, deterministic selection, constraints and fingerprints. The engine selects among explicit approved sites; it does not search arbitrary locations or establish a globally optimal/deployable count. Simplified UI must not invent real-site values or conceal incomplete/infeasible results.
- **Acceptance criteria:** Users can find the recommendation entry from the normal workspace; each disabled action explains the missing prerequisite and where to resolve it; recommendation from a valid approved pool shows count, identifiable selected sites and matching map markers; users can navigate between a result row and its site; zero/infeasible/partial outcomes are distinguishable from “not run”; changing significant inputs visibly invalidates the old result; constraints and graph-only limitations remain available.
- **Verification:** Production browser task walkthrough using unknown-input and approved test-only states; no-candidate, prohibited/locked candidate, infeasible, successful, stale, save/reopen and undo/redo cases; confirm displayed count equals selected candidate IDs and map coordinates equal approved candidates; Phase 6 service/API/frontend regressions and source integrity; verify existing Phase 7 CAP export semantics remain unaffected.
- **Contract impact:** Presentation-only clarification preserves Phase 6 scope. Free-space placement, invented operational defaults, RF guarantees, or a new optimization objective would change the accepted contract and require a separately scoped request. None is authorized by this item.
- **Route/open decisions:** Dedicated implementation contract for workflow and results presentation, preceded by a focused usability walkthrough. No new CAP calculation engine is proposed.

## Intake evidence and authorization history

2026-09-06: Recorded the user's eight requests in original order. Read map, workspace, IES association, CAP workflow source and relevant accepted decisions. Source review is evidence of current implementation structure, not proof of runtime success or root cause. All eight items await separate item-specific implementation authorization. No product files, source data, accepted contracts or seals were modified.

## Intake rules

Assign stable IDs `BL-001`, `BL-002`, and so on. Keep each item independently scoped; link dependencies and related items. Record unknowns explicitly and distinguish user reports from reproduced evidence. Clarification and prioritization do not imply implementation approval.

Recommend diagnosis when cause, reproduction, or contract impact is uncertain; a small corrective task for a bounded restoration of accepted behavior; or a dedicated implementation contract for new behavior, substantial cross-system changes, or changes to accepted contracts. All execution remains subject to separate item-specific authorization and applicable repository requirements.

Severity describes impact (critical / high / medium / low / not applicable); priority describes requested order (P0 urgent / P1 next / P2 normal / P3 deferred). Record a rationale and treat initial assessments as provisional. Do not invent urgency or a user decision.

## Per-item record template

- ID and title:
- Request date and user request:
- Type: bug / improvement / feature.
- User-visible problem or objective:
- Reproduction steps, environment, and observed behavior: or not applicable; unverified reports labeled explicitly.
- Expected behavior:
- Affected subsystem:
- Severity and rationale:
- Priority and rationale:
- Dependencies:
- Risks, including source preservation and accepted-behavior regressions:
- Acceptance criteria: observable, independently verifiable outcomes.
- Verification requirements: reproduction/regression checks, relevant automated tests, rendered workflow checks, source integrity, schema compatibility, and gate review as applicable; exact commands identified before execution.
- Changes an accepted Phase 1–7 contract: yes / no / unresolved, with affected contract sections or acceptance IDs and rationale.
- Recommended route: diagnosis / small corrective task / dedicated implementation contract, with rationale.
- Open questions:
- Status:
- Implementation authorization: not authorized unless an explicit user decision is recorded, including its date and scope.
- Evidence and decision history:

2026-09-06 live reproduction: user authorized the walkthrough and asked to continue. Updated BL-002/003/006/008 from observed browser/API behavior. Evidence: `harness/verify/2026-09-06-backlog-live-reproduction.md` and companion observations JSON. Test setup affected only isolated ignored runtime state; all product implementation remains unauthorized.

2026-09-06 planning handoff: user requested an implementation plan for Cursor on another computer. Proposed execution order and item designs are in [the implementation plan](superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md). Planning is authorized; implementation status remains unchanged until the user authorizes specific work items.

2026-09-07 BL-001 provider authorization: user selected the total-free EOX public WMTS option, required attribution, session-only choice, environment config (not project JSON), and explicit replaceability of the satellite provider later. Record: [provider authorization](post-roadmap-bl-001-provider-authorization-2026-09-07.md). Product implementation of BL-001 has not started.
