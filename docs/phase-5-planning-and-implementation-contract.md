# Phase 5 planning and implementation contract

Date: 2026-08-26
Status: planning authorized; implementation unauthorized
Controlling repository state: `c20b77b` (`docs: close Phase 4 after final QA pass`)

## 1. Authorization boundary and exclusions

This document is an implementation-ready plan, not authorization to implement. Phase 5 planning and every recommended decision in section 15 were explicitly approved on 2026-08-26. A later session may edit code only after separate explicit Phase 5 implementation authorization.

Phase 5 is limited to conceptual Wi-Fi visualization and deterministic area statistics:

- circles centered on unchanged existing customer poles;
- WIFI and SMART fixtures only; LITE never receives a circle;
- editable planning radius and enabled state;
- circle union, bounded aggregate overlap statistics, and optional analysis-area coverage/gap statistics;
- projected-metre geometry with WGS84 display rings;
- visible assumptions, warnings, provenance, and a permanent conceptual disclaimer.

It must not infer or calculate bands, antennas, EIRP, receiver sensitivity, throughput, capacity, channel plans, propagation loss, obstruction effects, interference, service quality, standards compliance, backhaul, CAP topology, or recommended pole/CAP placement. It must never create, move, redistribute, optimize, or delete customer poles. Phase 6 and later remain unauthorized.

The frozen 30 m value in `data/network/wifi-defaults.json` is an engineering assumption and must remain visibly editable. It is not a coverage guarantee.

## 2. Repository findings and reusable seams

The HEAD and clean worktree were verified before planning. Existing reusable seams are:

| Existing seam | Phase 5 use | Constraint |
|---|---|---|
| `backend/app/models.py` `Project`, `ProjectDefaults`, `PoleEdit`, `PoleFixtureConfiguration`, `LayerState` | Add typed Wi-Fi settings, analysis areas, result layer, and `wifi_coverage` gating | Keep source/pole edits/calculated/recommended layers separate; `extra="forbid"` remains authoritative |
| `backend/app/crs.py` | Transform source WGS84 coordinates to/from the selected projected CRS | All distance/area operations use a validated projected metre CRS |
| `backend/app/services/camera_geometry.py` | Reuse canonical ring, finite checks, WGS84 conversion, Shapely union/intersection patterns | Wi-Fi must have its own model/service and IDs; do not merge camera geometry |
| `backend/app/services/lighting_calculation.py` | Reuse input fingerprint/invalidation pattern and finite/performance guard style | Wi-Fi fingerprint includes all Wi-Fi-significant inputs, not lighting-only fields |
| `backend/app/services/configuration.py` and `main.py` | Capability validation, bulk target selection, save/open API error style | Wi-Fi overrides must be explicit and only valid for WIFI/SMART |
| `frontend/app/components/EngineeringWorkspace.tsx` | Existing edit/bulk/layer/area workflow and undo/redo | Add Wi-Fi controls without mutating source coordinates or other area collections |
| `frontend/app/components/EngineeringMap.tsx` | Add separate source/layers and visibility gate | Preserve red/yellow/blue fixture colors; use a distinct cyan/teal conceptual overlay |
| `frontend/app/lib/types.ts`, `api.ts` | Typed transport and persisted project shape | Regenerate/check `schemas/project.schema.json` and `schemas/openapi.json` only during authorized implementation |
| `backend/tests`, `frontend/tests/rendered-html.test.mjs` | Unit, API, migration, and rendered acceptance | Add tests for every geometry/statistics path and 74-pole workflow |

Current Wi-Fi configuration is only an untyped notes dictionary. Current `ProjectDefaults.wifi_radius_m` is already 30 m with bounds `(0, 1000]`; `LayerState.wifi_coverage` exists and defaults false. Current UI correctly says conceptual Wi-Fi is deferred. Current health response remains Phase 4 and must not be changed during planning.

## 3. Confirmed facts, assumptions, and blocked decisions

### Confirmed

- Existing-pole mode is mandatory and source coordinates, raw coordinate text, source IDs, and uploaded bytes are authoritative.
- The supplied KML contains 74 valid WGS84 point placemarks; the imported engineering CRS is normally `EPSG:32617`.
- LITE provides no Wi-Fi; WIFI and SMART provide Wi-Fi according to the frozen fixture-type catalog.
- `data/network/wifi-defaults.json` is `conceptual_circle`, radius 30 m, with explicit excluded RF factors and disclaimer.
- WGS84 is display/interchange only; project distance and area work uses the validated projected CRS.
- Phase 3 and Phase 4 already establish deterministic projected geometry, WGS84 output, separate calculated layers, provenance, and stale-result patterns.

### Recommended assumptions for approval

- A circle is a Euclidean projected-plane buffer around the effective source-pole point, independent of pole height, fixture model, camera, lighting, terrain, or obstacles.
- Default radius is project-wide and per-pole override is nullable: null means inherit the project default; a numeric override is explicit.
- Eligible pole default is enabled for WIFI/SMART when a valid fixture classification/model capability says Wi-Fi is provided; ineligible or LITE poles are excluded regardless of stale settings.
- “No analysis boundary” is a safe normal state: circles and global metrics may be calculated, but boundary/gap metrics are `unavailable`, never inferred from source extents or other polygons.
- Use a separate `wifi_analysis_areas` collection rather than reusing `priority_areas` or `calculation_areas`.

### Blocked until user approval

The recommendations are concrete, but they are not silently ratified as product decisions. The choices and consequences are listed in section 15. At minimum, the user must approve the separate analysis-area workflow, effective-radius/enable semantics, numeric limits, and additive version change before implementation.

## 4. Recommended data model

All new models are strict, finite, JSON-safe Pydantic models. IDs are stable strings and are never derived from mutable display names.

| Model/field | Contract |
|---|---|
| `ProjectDefaults.wifi_radius_m` | Existing field; retain default `30.0`, `0 < value <= 1000`, finite; label `engineering_assumption`, unit metres, conceptual disclaimer |
| `PoleWifiConfiguration` | New typed replacement for the Wi-Fi portion of the untyped dictionary: `radius_override_m: float \| None`, `enabled: bool \| None`, `notes: str`, `modified_at`, and `configuration_revision: int >= 1` |
| `PoleFixtureConfiguration.wifi_configuration` | `PoleWifiConfiguration \| None`; null for no Wi-Fi configuration. Existing notes must migrate losslessly into `notes`; unknown legacy keys go under a preserved `legacy_metadata` map or migration warning, never disappear |
| `WifiAnalysisArea` | `id`, `name` 1–120 chars, closed WGS84 ring, finite in-range coordinates, at least 3 distinct vertices, valid/non-degenerate projected polygon, `created_at`, `modified_at`, `polygon_revision >= 1` |
| `WifiCoverageState` | `status: not-calculated/calculated/warning/error`, `last_calculated_at`, `warnings`, `assumptions`, `provenance`, `calculation_input_sha256`, `model_version` |
| `WifiCoverageResult` | Separate result layer containing ordered circle records, global statistics, per-analysis-area statistics, fingerprint, projected CRS, model/version, warnings, assumptions, and disclaimer |
| `WifiCircle` | Stable ID `wifi-circle/<source_pole_id>`; `pole_id`, effective fixture type, center projected metres, explicit `projected_ring`, WGS84 display ring, effective radius, enabled/eligible flags, source/effective provenance, area m², approximation parameters |
| `Project.wifi_analysis_areas` | Separate collection; never inferred from camera or lighting collections |
| `Project.wifi_coverage` | Separate calculated object; never stored in `camera_geometry`, `lighting_calculations`, `calculated_layers`, or `recommended_layers` |

Effective value rules:

1. Start with the source pole ID and effective fixture type/active state from `effectivePole` semantics.
2. A pole contributes only if active, effective type is WIFI or SMART, and the authoritative fixture model capability (when a model is assigned) has `wifi=true`. A capability conflict is an error/warning and contributes nothing; LITE always contributes nothing.
3. Radius is `pole override` when non-null, otherwise `project.defaults.wifi_radius_m`.
4. Enabled is `pole enabled` when non-null, otherwise `true` for eligible WIFI/SMART poles.
5. `enabled=false` suppresses the circle but retains the configuration and provenance. Clearing the override restores inheritance; it does not copy the default into pole data.
6. An explicit fixture-model replacement creates a new capability-specific configuration baseline, following the established Phase 2 lifecycle. It does not carry incompatible Wi-Fi configuration across models; the replacement is atomically validated against the selected model and fixture type. A fixture-type/model mismatch is rejected, not hidden or deferred.
7. Bulk edits target all/folder/manual pole IDs, validate all targets before mutation, and support set radius, clear radius override, set enabled, clear enabled override, and notes. Null/omitted means unchanged, following existing bulk semantics.

Every user edit increments the pole Wi-Fi configuration revision and records `modified_at`; project default and analysis-area changes update project timestamps. The source remains byte-for-byte unchanged.

## 5. Deterministic geometry

The calculation service should be `backend/app/services/wifi_coverage.py`, pure over a validated `Project` plus no external RF inputs.

For each eligible enabled pole, transform the exact effective coordinate to `(x, y)` in the validated project CRS: use the source WGS84 coordinate unless an explicit `location_edit_authorized=true` edit supplies an effective coordinate. Preserve and record the source coordinate alongside the effective coordinate in provenance. Reject non-finite input/output.

Construct a true projected circle as a Shapely buffer centered at `(x, y)` with radius `r`. Recommended approximation contract: `resolution=32` segments per quarter (128-sided ring plus the repeated closing vertex), fixed for model version `conceptual-circle-1.0.0`; use `quad_segs=32` if supported by the installed Shapely API. This is deterministic and materially bounded. Persist both `projected_ring` and a separately transformed WGS84 display ring for reproducibility. Do not calculate area from WGS84 degrees.

Canonicalization:

- round persisted projected coordinates to 9 decimal places and WGS84 display coordinates to 10 decimal places, matching the existing camera convention;
- QA numeric contract: projected/WGS84 coordinates must be within `1e-9 m`/`1e-10 degrees` absolute of the unrounded deterministic transform; persisted areas and lengths are rounded to 6 decimals and must be within `1e-6 m²`/`1e-6 m` absolute of the unrounded projected calculation; persisted percentages are rounded to 6 decimals and must be within `1e-5` percentage points; synthetic reference comparisons use the same tolerances;
- normalize ring to counter-clockwise, rotate to the lexicographically smallest rounded vertex, and close it by repeating the first vertex;
- reject non-finite centers/radii/ring vertices, invalid or empty geometry, radius outside approved bounds, and area below `1e-8 m²`;
- circle IDs are `wifi-circle/<pole_id>`; duplicate source IDs are already forbidden by `Project` validation;
- order circles by source `sequence_index`, then pole ID; order area summaries by stored area order; order candidate pairs lexicographically by canonical circle IDs.

The approximation tolerance is documented as the maximum geometric approximation choice, not RF accuracy. The UI must call the ring “conceptual circle approximation” if showing vertices.

## 6. Statistics and equations

Let (C_i) be each valid enabled conceptual circle in projected metres and (A_i = area(C_i)). Let (U = union_i C_i).

MVP overlap output and performance:

- Persist aggregate overlap statistics only: total pairwise overlap area, total multiply-covered union area, and overlap-pair count. Do not persist every pair geometry. Maximum overlap multiplicity and the exact multiplicity histogram are both deferred unless separately approved with their own performance contract.
- Use an STRtree/spatial index (or the installed Shapely equivalent) to generate candidate circle pairs, then compute exact projected intersections only for candidates. Deterministically order candidates by canonical circle IDs. If candidate pairs requiring intersection exceed 50,000, return HTTP 422 and preserve the prior project/result.
- Recommended hard caps pending approval: 500 eligible circles, 128 closed-ring vertices per circle, 64,500 total persisted circle-ring vertices (`500 × 129`, strictly below the 250,000 total persisted-geometry-vertex limit), 50,000 candidate-pair/intersection operations, 200 analysis areas, 10,000 vertices per analysis area, and 250,000 total persisted geometry vertices. The supplied 74-pole project has at most `74 × 73 / 2 = 2,701` unordered circle pairs.
- Reject a request that exceeds any cap with HTTP 422, identify the violated cap, preserve the prior saved project/result, and never silently drop circles, pairs, vertices, or change radii. The supplied 74-pole project is comfortably below the 500-circle and 64,500-circle-vertex caps.
- Maximum overlap multiplicity, the exact multiplicity histogram, and persisted pair records are out of MVP scope and require separate approval with a performance/storage contract.

Global statistics:

- `circle_count = n`;
- `individual_area_m2 = Σ A_i` (sum of per-circle areas; may double-count overlaps);
- `union_covered_area_m2 = area(U)` (no double counting);
- `overlap_area_m2 = Σ A_i - area(U)` (non-negative within tolerance);
- `pairwise_overlap_area_m2` is the aggregate sum of `area(C_i ∩ C_j)` over intersecting candidate pairs above `1e-8 m²`; it intentionally double-counts regions covered by 3+ circles across pairs;
- `multiply_covered_union_area_m2 = area(unary_union({C_i ∩ C_j | i < j and area(C_i ∩ C_j) > 1e-8 m²}))`; the set contains every non-empty candidate-pair intersection geometry above tolerance, and this unary union is exactly the region covered by at least two circles; it is an aggregate only.

Percentages are only reported when a positive denominator exists: `union_over_individual_percentage = 100 * union_covered_area_m2 / individual_area_m2`; otherwise null. No “coverage percentage” is shown without an explicit analysis polygon.

For each valid `WifiAnalysisArea` polygon (P_j), use projected geometry and:

- `area_m2 = area(P_j)`;
- `covered_area_m2 = area(U ∩ P_j)`;
- `uncovered_area_m2 = area(P_j - U)`;
- `covered_percentage = 100 * covered_area_m2 / area_m2`;
- `uncovered_percentage = 100 * uncovered_area_m2 / area_m2`;
- boundary coverage is a line metric, not area: `boundary_covered_length_m = length(boundary(P_j) ∩ boundary(U))` is not sufficient for a circle crossing boundary. Recommended semantics are the fraction of boundary line segments within the union, computed by `boundary(P_j).intersection(U).length`; `boundary_covered_percentage = 100 * that length / boundary(P_j).length`.

If there is no analysis area, all per-area metrics are absent and the UI says “Boundary/gap statistics unavailable — draw a Wi-Fi analysis area.” User-created or edited invalid areas must never be persisted: return HTTP 422 and preserve the prior valid polygon/result. A corrupt stored JSON area is different: GET/open returns controlled HTTP 422 identifying the corrupt stored project and does not replace it. There are no legacy Wi-Fi areas in schema 2.4.0. Zero circles yields zero covered area, full uncovered area within a valid polygon, and 0% boundary coverage; null is reserved for undefined denominators or unavailable boundaries.

## 7. Analysis-area safeguards

Validate WGS84 ring shape using the same closed/finite/bounds/non-self-intersecting policy as existing areas, then validate the projected polygon. Recommended hard limits requiring approval: 200 analysis areas per project, 10,000 vertices per area, 500 eligible circles, 128 closed-ring vertices per circle, 50,000 candidate-pair/intersection operations, and 250,000 total persisted geometry vertices. The circle budget is `500 × 129 = 64,500` vertices including each closing vertex, leaving headroom for analysis-area rings. Reject requests over limits with 422 and preserve the previous saved state.

Use Shapely vector geometry for union/intersection. Reject non-finite transformed coordinates and geometry errors; catch topology and arithmetic errors and return a readable warning/error result, never partial metrics. Do not silently simplify, drop vertices, change radius, or downgrade statistics. A future implementation may add an explicitly versioned safe simplification policy only with approval.

## 8. Fingerprints and stale-result lifecycle

Implement `wifi_calculation_input_sha256(project)` using canonical JSON (`sort_keys=true`, compact separators, `allow_nan=false`) and SHA-256. Include:

- Wi-Fi model version and circle approximation parameters;
- project ID only if product chooses project-specific identity; otherwise exclude it for reproducibility;
- selected projected CRS and source CRS;
- project default radius;
- every source pole ID, sequence index, exact source coordinate, exact effective coordinate, effective fixture type, active state;
- exact assigned fixture model ID/revision and `capabilities.wifi` when present;
- exact effective radius and enabled state. Exclude notes, `modified_at`, and the general `configuration_revision`; they are not geometry inputs. If an implementation needs a revision, add a separate geometry-significant revision incremented only for effective radius/enabled changes, but fingerprinting exact effective inputs is preferred;
- every Wi-Fi analysis-area ID, polygon revision, name if displayed in result, and exact WGS84 ring;
- numeric safety limits that affect output, including the 50,000 candidate-pair/intersection cap.

Invalidate and remove Wi-Fi results, reset coverage state to `not-calculated`, and clear derived provenance on any change to source origin/effective coordinate, fixture type/model/capability, active state, project CRS, default radius, per-pole radius override, per-pole enabled override/effective enabled state, or analysis-area geometry/name if names are persisted in summaries. Notes, `modified_at`, and general configuration revision changes alone do not invalidate geometry. Notes remain live user configuration and are shown from the current pole edit, not copied into calculated-result provenance.

Apply invalidation in frontend mutation paths, backend PUT/open/save, bulk configuration, area create/edit/redraw/delete, and GET/open revalidation. A stale result must never be displayed as current after reopen. Changing only layer visibility must not invalidate.

## 9. API and error contracts

Use existing response/error style: successful responses return the complete `Project`; controlled validation failures return HTTP 422 with a readable `detail`; missing project returns 404; path/body ID mismatch returns 409. Do not add an API that mutates source files or pole coordinates.

Recommended endpoints:

| Method/path | Purpose |
|---|---|
| `PUT /api/projects/{id}` | Save typed project, validate capabilities, invalidate stale Wi-Fi, persist, return project |
| `POST /api/projects/open` | Migrate/validate legacy project, preserve source bytes, invalidate stale Wi-Fi, return project |
| `PATCH /api/projects/{id}/poles/bulk` | Extend existing typed bulk patch for Wi-Fi set/clear radius and enabled override/notes |
| `POST /api/projects/{id}/wifi-coverage/calculate` | Calculate all current circles and all valid analysis areas; save result and return project |
| `POST /api/projects/{id}/wifi-coverage/invalidate` | Optional explicit UI action; safe idempotent stale reset |

Do not expose a separate “RF prediction” endpoint. `calculate` must fail 422 when no projected CRS exists, when a selected radius is invalid, or when geometry exceeds approved limits. It may succeed with zero circles and no analysis areas, returning a warning-state conceptual result. Geometry errors identify the pole or area ID and preserve the last saved project/result on failed mutation.

The result must include `model_version`, `projected_crs`, approximation resolution, `calculation_input_sha256`, exact effective-value provenance, warnings, assumptions, and the exact disclaimer: “Conceptual geometric visualization only; not verified RF coverage, performance, capacity, service quality, or standards compliance.”

## 10. UI and map workflow

Extend `EngineeringWorkspace` with a clearly marked “Phase 5 — Conceptual Wi-Fi” panel:

- project default radius input in metres, showing “engineering assumption” and the 30 m source/default;
- per-pole Wi-Fi controls in `PoleInspector` for eligible WIFI/SMART poles: enabled/inherit toggle, radius override/restore-default, notes, effective value, and provenance;
- bulk controls for selected all/folder/manual poles with explicit set/clear actions and all-target validation;
- “Draw Wi-Fi analysis area”, edit settings/name, redraw-from-empty, delete, select, and “Calculate conceptual Wi-Fi” controls;
- result table with counts, individual sum, no-double-count union, aggregate pairwise/multiply-covered overlap, and per-area covered/uncovered/boundary statistics; maximum multiplicity and exact multiplicity histogram are deferred and not displayed in MVP;
- empty-state wording when no boundary exists; no inferred source bounding box;
- warnings list entries for ineligible/stale/invalid geometry and all conceptual disclaimers.

Map additions in `EngineeringMap.tsx`:

- separate GeoJSON sources for conceptual circles, overlap visualization (if shown), analysis areas, and drafts;
- circle fill/line in a distinct cyan/teal family with reduced opacity; do not reuse LITE red, WIFI yellow, SMART blue, camera purple/cyan, lighting teal heat-map semantics, or CAP colors;
- preserve fixture marker colors exactly: LITE red, WIFI yellow, SMART blue;
- layer panel enables `wifi_coverage` only after a valid calculated result, but the control label always includes “Conceptual Wi-Fi”; default remains false until an explicit user toggle;
- popups/inspector show pole ID, source coordinate provenance, effective radius, enabled state, conceptual disclaimer, and no RF claims.

Analysis-area drawing must follow the existing safe draft pattern: new/redraw starts empty, prior saved geometry remains until the replacement validates, and invalid drafts do not mutate or become persisted authoritative input. Save/reopen must preserve geometry, settings, result fingerprint, warnings, and layer state.

Export boundary: existing updated KML export may continue to export source poles/fixture edits only. Do not silently export conceptual circles as customer pole data. A future explicit Wi-Fi export is out of Phase 5 unless separately approved.

## 11. Migration and versioning strategy

Recommended additive versions, pending approval:

- project schema `2.5.0` from `2.4.0`;
- software/API `0.5.0`;
- Wi-Fi calculation model `conceptual-circle-1.0.0`;
- typed Wi-Fi configuration contract `1.0.0`.

The compatibility rationale is additive and lossless: existing 2.4.0 projects gain empty `wifi_analysis_areas` and an empty/not-calculated `wifi_coverage`; existing `defaults.wifi_radius_m` remains 30 m; existing untyped `wifi_configuration.notes` is copied into the typed `notes`; no source bytes, coordinates, fixture assignments, camera results, lighting areas/results, or unknown legacy keys are discarded. A schema bump is required because strict `Project` validation and generated JSON/OpenAPI contracts change. A minor version, rather than patch, is appropriate because new persisted fields and API behavior are introduced while old fields remain readable. Notes are not copied into calculated-result provenance and do not affect the geometry fingerprint.

Migration must accept `2.4.0` and all already-supported versions through the existing migration chain, then add Phase 5 defaults. It must reject unsupported versions, preserve the original payload until the migrated model validates, and add an assumption stating that the Wi-Fi result is not calculated. Existing projects must not gain inferred analysis polygons or circles merely by opening them. The migration must be idempotent and tested byte-for-byte for source content and coordinate equality.

Do not change frozen catalog versions or `data/network/wifi-defaults.json` during implementation. If the user rejects 2.5.0/0.5.0, stop and record the approved alternative before coding.

## 12. Likely implementation files and sequence

1. Governance: resolve section 15, update status/decision log, then authorize implementation separately.
2. Backend models: `backend/app/models.py`; add typed Wi-Fi models, collections, result contracts, version constants, validators, migration defaults.
3. Wi-Fi service: add `backend/app/services/wifi_coverage.py`; implement canonical rings, projected buffers, union/partition statistics, analysis clipping, fingerprints, stale invalidation, limits, and warnings.
4. Configuration: `backend/app/services/configuration.py`; validate capability/radius/enable semantics and extend bulk patch with explicit clear operations.
5. API: `backend/app/main.py`; add calculation endpoint, invoke stale invalidation in save/open/bulk/get paths, update API description/version only after approval.
6. Generated contracts: run `backend/scripts/export_schema.py`; review only `schemas/project.schema.json` and `schemas/openapi.json` changes.
7. Backend tests: add `backend/tests/test_phase5_wifi_coverage.py`, migration cases in `backend/tests/test_models.py` or a focused migration test, and API cases in `backend/tests/test_api.py`.
8. Frontend types/transport: `frontend/app/lib/types.ts`, `frontend/app/lib/api.ts`, and a small `frontend/app/lib/phase5-workflows.mjs` for draft validation/effective-value/invalidation helpers.
9. Frontend controls: `frontend/app/components/PoleInspector.tsx`, `EngineeringWorkspace.tsx`, `EngineeringMap.tsx`, and `frontend/app/globals.css` for distinct styling.
10. Frontend tests: `frontend/tests/rendered-html.test.mjs` plus strict TypeScript/lint/build.
11. Integration/rendered acceptance: use supplied 74-pole KML, draw an explicit analysis area, calculate, save/reopen, toggle layers, verify all prior camera/lighting collections remain separate.

## 13. Acceptance matrix

| ID | Type | Acceptance |
|---|---|---|
| G-01 | Geometry unit | One 30 m projected circle has deterministic ID, finite canonical closed ring, stable area within the approved buffer approximation, correct WGS84 transform, and no source mutation |
| G-02 | Geometry unit | LITE is excluded; WIFI/SMART eligible poles contribute; inactive poles and disabled overrides do not contribute; capability conflicts warn and exclude |
| G-03 | Geometry unit | Radius inheritance, override, clear/restore, enable inheritance, explicit disable, and bulk set/clear semantics are exact |
| G-04 | Geometry unit | Non-finite, zero, negative, >maximum, topology-invalid, and projected non-metre inputs return controlled errors without partial mutation |
| S-01 | Statistics unit | Two disjoint circles: sum equals union and aggregate overlap is zero |
| S-02 | Statistics unit | Two overlapping circles: pairwise area, union, overlap, multiply-covered area, and percentages match synthetic analytic/Shapely reference within documented tolerance |
| S-03 | Statistics unit | Three circles validate pairwise double-counting versus the exact multiply-covered union without requiring multiplicity outputs |
| S-04 | Statistics unit | Valid analysis polygon clips covered/uncovered area and boundary length; no area uses no inferred boundary; zero circles produce full uncovered valid-area metrics |
| S-05 | Safety unit | Vertex/circle/total-vertex and 50,000 candidate-pair/intersection limits, huge radii, invalid bounds, and topology errors are deterministic 422 responses preserving the prior result |
| F-01 | Fingerprint unit | Every listed significant change invalidates; notes/layer visibility do not invalidate geometry; stale result is removed on save/open/get |
| M-01 | Migration | 2.4.0 and each supported legacy version open to the new schema with exact source bytes, raw coordinate text, coordinates, IDs, camera data, and lighting data preserved; migration is idempotent |
| A-01 | API | Calculate returns complete typed project/result, warnings/disclaimer/provenance, 404/409/422 contracts, and no endpoint changes source bytes or coordinates |
| A-02 | API | Failed area/radius/capability edits leave saved project/result unchanged; successful changes stale result before recalculate |
| R-01 | Rendered UI | 74-pole supplied KML shows unchanged red/yellow/blue fixtures, distinct conceptual overlay, default 30 m assumption, editable effective values, and no RF claim |
| R-02 | Rendered UI | No-analysis-area state shows circles/global metrics only and explicitly says gap/boundary statistics unavailable; no source extent is used |
| R-03 | Rendered UI | Draw/redraw/edit/delete/save/reopen of analysis areas works; invalid replacement preserves prior polygon/result |
| R-04 | Rendered UI | Camera priority areas and lighting calculation areas remain visible/functional and separate from Wi-Fi areas/results; Phase 6 CAP remains gated |
| R-05 | Production | TypeScript, ESLint, production build, complete backend suite, rendered suite, and zero new browser-console errors pass |

## 14. Independent QA gate criteria

The Phase 5 implementation cannot be accepted until an independent reviewer confirms: all blocking decisions are recorded; generated contracts are fresh; migrations are lossless and idempotent; geometry/statistics tests cover synthetic cases and limits; the supplied 74-pole source remains byte/coordinate identical; stale-result invalidation covers every listed mutation; layer separation and fixture colors are preserved; all UI copy is explicitly conceptual; no RF factors or CAP recommendations were inferred; and the production-rendered workflow passes with no regressions to Phases 1–4. The reviewer must issue a separate PASS/FAIL decision document before Phase 6 planning or implementation is considered.

## 15. Approved planning decisions

The user explicitly approved every recommended choice below on 2026-08-26. These decisions are binding implementation scope. This decision approval does not authorize implementation, which remains a separate gate.

| Decision | Recommended choice | Consequence if approved | Consequence if changed/omitted |
|---|---|---|---|
| Analysis boundary | Add separate user-drawn `wifi_analysis_areas`; no inferred boundary | Enables honest gap, covered/uncovered, and boundary statistics; adds polygon UI/model/migration | Without it, only global circle/overlap metrics are available; no gap claims |
| Default eligibility | Eligible WIFI/SMART defaults enabled; LITE always excluded; capability conflict excludes with warning | Existing classifications visualize immediately after calculate while remaining editable | Requiring explicit enable adds configuration burden and changes rendered acceptance |
| Override hierarchy | Project default → nullable per-pole radius override; nullable per-pole enabled override; explicit clear restores inheritance; model replacement starts a new compatible baseline | Stable provenance, predictable bulk behavior, and established Phase 2 lifecycle | Copying defaults or incompatible settings across models makes restore ambiguous and risks invalid capability state |
| Radius limits/precision | Keep 30 m default; max 1000 m; 128-sided circles; 9-decimal projected/10-decimal WGS84 persistence; hard project limits in section 7 | Deterministic and bounded performance | Different limits/resolution alter schema/model version, metrics, and QA tolerances |
| MVP overlap output | Persist aggregate pairwise overlap area, exact unary-union multiply-covered area, and overlap-pair count; use an STRtree; no pair geometries, maximum multiplicity, or exact histogram; cap candidate intersections at 50,000 and circles/vertices as specified | Keeps required overlap/gap capability bounded and makes 74-pole acceptance practical; 74 poles yield at most 2,701 unordered pairs | Maximum multiplicity, exact histograms, or pair records require separate approval with a performance/storage contract, limits, and QA scope |
| Boundary line metric | Boundary covered means `boundary(P) ∩ union(C)` length fraction | Produces a reproducible line statistic separate from area coverage | A different segment/intersection definition changes reported “boundary coverage” |
| Versioning | Project 2.5.0, software/API 0.5.0, model 1.0.0 | Makes additive persisted/API behavior explicit and generated contracts reviewable | Any alternative needs a compatibility rationale and migration rewrite |
| Export | Keep conceptual circles/results out of updated KML; JSON remains authoritative archive | Prevents conceptual geometry from being mistaken for customer pole data | Explicit additional export needs a new approved product contract |
| Approval gate | Separate explicit implementation authorization after all rows above are resolved | Prevents planning text from being mistaken for implementation permission | No coding session may proceed safely |
