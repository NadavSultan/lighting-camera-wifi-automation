# Phase 3 Integration Review and QA Report

Review date: 2026-08-16

Project: Lighting Camera WiFi Automation

Scope: Phase 3 — Camera Geometry

Implementation reviewed: `c8814587d08731cbb5e125d644b6a55f67483d48`

Completion-report commit reviewed: `ecc4022`

Review type: independent integration review and QA

Final gate: **FAIL**

Phase 4 authorization: **NO — Phase 4 may not begin.**

## 1. Executive conclusion

Phase 3 does not pass its independent acceptance gate. The fixed-mount camera calculation itself is substantially correct and reproducible: the approved Phoenix 1 and Solitaire orientations, zero optical-center offsets, 35-degree downward tilt, coupled fixture rotation, projected flat-ground pinhole intersection, all three lenses, invalid-ray policy, overlaps, priority-area union math, null pixel-density boundary, coordinate preservation, and later-phase gating all passed independent checks.

Two Major defects prevent acceptance:

1. Priority-area editing does not implement replacement geometry as presented. The edit action preloads the old vertices and then appends newly clicked “replacement” vertices. A normal rectangular replacement produced an eight-vertex self-intersecting polygon, persisted it, and reduced the summary to `0.0 / 0.0 m²` with an invalid/degenerate warning.
2. The checked-in project JSON Schema and OpenAPI document are stale. Both omit the runtime `PriorityAreaCoverageSummary.warnings` field. The three operational catalog schemas are current, but the completion report's generated-contract freshness claim is false for `schemas/project.schema.json` and `schemas/openapi.json`.

No Blocker or Critical defect was found. Two Moderate, two Minor, and one Advisory finding are also recorded below. No finding was fixed during QA, and no Phase 4 work was begun.

## 2. Review basis and independence

The audit began read-only. The worktree was clean at start. The following controlling material was reviewed before testing:

- `AGENTS.md` and every required startup document in its prescribed order.
- The complete Phase 2 gate record: original completion report, independent FAIL, corrective completion report, corrective retest, retrospective contract ratification, NIR-01 completion note, and final unconditional-pass retest.
- Phase 3 authorization and decisions DL-006 through DL-008.
- Coordinate, camera, calculation-area, data-model, architecture, schema-contract, assumptions, open-question, and risk documentation.
- Phase 3 implementation, operational catalogs, migrations, backend and frontend tests, checked-in JSON Schemas, and OpenAPI.
- Commit identity, history, and the implementation/completion-report diffs.

The Phase 3 completion report was treated only as a claim set. Automated suites, independent in-memory contract comparisons, independent calculations, adversarial cases, and a rendered browser workflow were rerun. Isolated runtime project and catalog directories and nonstandard ports were used. The repository remained clean until this report was added.

## 3. Findings

### P3-IR-01 — Major — Priority-area edit appends to existing geometry instead of replacing it

The edit workflow initializes `priorityDraft` with the existing ring's vertices in `frontend/app/components/EngineeringWorkspace.tsx`, while the UI says to click replacement vertices and the map handler always appends clicks. There is no clear/replace transition before new geometry is captured.

Rendered reproduction:

1. Drew a four-vertex rectangle named `QA priority area`.
2. Saved it and obtained a valid summary: `9,377.1 / 30,386.8 m² · 30.9%`.
3. Clicked **Edit**, renamed it, and clicked four replacement rectangle vertices.
4. Saved the edit.
5. The persisted ring contained the four old vertices followed by the four new vertices and closure, creating a self-intersecting polygon.
6. The application displayed `0.0 / 0.0 m² · 0.0%`; the persisted summary warning was `Priority-area polygon is invalid or degenerate in the projected CRS; no intersection was calculated.`

Delete worked, and drawing a fresh area after deletion worked. The defect is specifically the required edit workflow and therefore fails requirement 22.

Relevant implementation: `frontend/app/components/EngineeringWorkspace.tsx:246`, `frontend/app/components/EngineeringWorkspace.tsx:250`, `frontend/app/components/EngineeringWorkspace.tsx:252`, and `frontend/app/components/EngineeringWorkspace.tsx:352`.

### P3-IR-02 — Major — Checked-in project schema and OpenAPI are stale

An independent in-memory generation comparison produced:

| Contract | Fresh |
|---|---:|
| `project.schema.json` | No |
| `openapi.json` | No |
| `fixture-model-catalog.schema.json` | Yes |
| `ies-library.schema.json` | Yes |
| `camera-equipment-catalog.schema.json` | Yes |

The runtime model defines `PriorityAreaCoverageSummary.warnings` at `backend/app/models.py:248`. The checked-in `PriorityAreaCoverageSummary` definitions in `schemas/project.schema.json:847` and `schemas/openapi.json:2809` omit that property. Regenerating in memory shows exactly the missing string-array property in both documents; no other drift was found.

This contradicts the completion report's schema-freshness claim and fails the required generated-schema/OpenAPI freshness comparison in requirement 3. Runtime responses can contain a field that the published contracts do not describe.

### P3-IR-03 — Moderate — Camera warnings are not represented by the map warning layer

The rendered map clearly distinguishes camera 1, camera 2, overlaps, and priority areas. It does not provide a camera-warning map source or layer. The visible **Warnings** layer checkbox is not included in `EngineeringMap` layer visibility state, and the global validation list renders only `project.warnings`, not camera footprint warnings.

With Phoenix SMART assigned but height and lenses missing, both camera slots showed clear warnings only in the selected-pole inspector while the map-layer validation summary still reported `0 warnings`. The user must select the affected pole to discover the camera warning. This only partially satisfies requirement 19.

Relevant implementation: `frontend/app/components/EngineeringMap.tsx`, `frontend/app/components/EngineeringWorkspace.tsx:345`, and `frontend/app/components/PoleInspector.tsx:86`.

### P3-IR-04 — Moderate — Stored footprint provenance omits the actual H/V FOV inputs and mounting-contract version

Each footprint records fixture/model/template/camera/lens revision IDs, height, azimuths, fixed tilt, zero offsets, CRS, geometry version, assumptions, warnings, geometries, area, and pixel-density state. It does not snapshot the `horizontal_fov_deg` and `vertical_fov_deg` values actually used, nor the mounting template's `geometry_contract_version`.

Those inputs are consumed by `camera_geometry.py` but are absent from `CameraFootprintResult`. A portable project therefore requires an external operational catalog history to reproduce the exact ray inputs rather than carrying complete calculation inputs in the result itself. This is a provenance completeness gap against requirement 18, not a demonstrated geometry error.

### P3-IR-05 — Minor — Absolute azimuth is rendered with floating-point noise

After entering fixture azimuth `121.889°`, the two Phoenix results were mathematically correct at `51.889°` and `191.889°`, preserving 140-degree separation. The inspector rendered camera 1 as `51.888999999999996°` because the result is displayed without formatting.

Backend normalization is correct; this is a precision/presentation defect in `frontend/app/components/PoleInspector.tsx:84`.

### P3-IR-06 — Minor — Camera convention and assumption documents contradict the approved Phase 3 decision

DL-007 and the implementation approve immutable zero XYZ optical-center offsets. However:

- `docs/camera-conventions.md:11` says physical XYZ offsets remain undefined and must be approved before Phase 3 geometry.
- `docs/camera-conventions.md:31` repeats that the offsets remain unknown.
- Its future-prerequisite section still says Phase 3 must not start until physical offsets and terrain are approved.
- `docs/engineering-assumptions.md:32` continues to list mounting position/offsets among values requiring future validation without distinguishing the approved MVP zero-offset contract.

The controlling decision log, risk register, catalogs, and runtime are consistent, so this is classified Minor documentation drift rather than an implementation ambiguity.

### P3-IR-07 — Advisory — Existing non-failing toolchain warnings remain

The backend emitted the existing Starlette/httpx2 deprecation warning. The production build emitted the existing MapLibre chunk-size advisory and Vinext route-classification advisory. None affected the reviewed behavior.

## 4. Requirement traceability

| # | Requirement | Result | Independent evidence |
|---:|---|---|---|
| 1 | Preserve pole coordinates, IDs, raw strings, metadata, uploads, and edit separation | PASS | All 74 complete source-pole tuples and the embedded source hash remained exact through assignments, geometry, priority data, save, and reopen. Only two pole-edit overlay keys were added. |
| 2 | Preserve seven Phase 1 catalogs and every `Input/` file | PASS | Byte-for-byte Git diff against the accepted Phase 2 gate commit `9f7f91f` was empty; engineering/source validator passed. |
| 3 | Additive schemas, current generated contracts, lossless migrations | FAIL | Project `2.2.0` and fixture catalog `1.2.0` are additive and migrations preserve data, but project schema/OpenAPI freshness fails (P3-IR-02). |
| 4 | Phoenix fixed -70/+70 | PASS | Catalog validation, direct inspection, backend cases, and rendered 290/70 then 51.889/191.889 results. |
| 5 | Solitaire fixed -60/+60 | PASS | Catalog validation and rendered 300/60 results. |
| 6 | Fixed 35-degree tilt and zero offsets | PASS | Current template r2, runtime provenance, contract validation, and calculations agree. |
| 7 | Optical-center height equals configured height | PASS | Service origin uses pole projected X/Y and configured/default height Z; independent areas scale correctly. |
| 8 | Fixture azimuth rotates cameras together | PASS | Rendered Phoenix rotation retained exactly 140-degree separation; backend rotation tests passed. |
| 9 | No per-camera azimuth/tilt editing | PASS | Both fields are disabled inherited values; source and rendered tests expose only fixture azimuth and explicit legacy reset. |
| 10 | Preserve legacy overrides and block FOV | PASS | Migration retains both legacy fields and metadata exactly; calculation returns no polygon with explicit reset warning. |
| 11 | Normalize across 0/360 | PASS WITH MINOR | Backend cases including 350°, 359°, and 360° pass; UI formatting defect is P3-IR-05. |
| 12 | Projected-metre pinhole/frustum flat-ground calculation | PASS | `EPSG:32617`, metre axes, documented basis, independent formula comparison, and Shapely areas agree. |
| 13 | Safe invalid/degenerate rays | PASS | Horizontal, upward, exact-boundary, NaN, infinity, invalid FOV, zero height, and micro-degenerate cases all returned no polygon with deterministic errors. |
| 14 | Reproduce all three approved lenses | PASS | Independent 10 m areas: JL-LN039 `241.641980 m²`; JL-LN042 `1,146.954644 m²`; JL-LN037 `89,376.460900 m²`; service matched within `1e-6 m²`. |
| 15 | Missing input/revision/contract warning policy | PASS | Height, lens, camera/lens revision, fixture/template revision, and legacy mounting contract cases yield no footprint and clear warnings. |
| 16 | Disabled camera has no polygon and no error | PASS | Rendered camera 2 disable reduced valid count by one; result retained no polygon and an empty warning list. |
| 17 | LITE/WIFI have no camera geometry | PASS | Capability/UI inspection and service control flow confirm no footprint results. |
| 18 | Complete footprint provenance | PARTIAL | Most provenance is present; actual H/V FOV inputs and mounting-contract version are omitted (P3-IR-04). |
| 19 | Distinct camera/overlap/priority/warning map styling | PARTIAL | Camera 1 purple, camera 2 cyan, overlap pink, and priority amber pass. Camera warnings have no map representation (P3-IR-03). |
| 20 | Pairwise overlap in projected m² and labeled totals | PASS | Two overlap pairs totaled `483.283960 m²`; UI explicitly labels “summed pairwise overlap.” |
| 21 | Priority covered union avoids double count | PASS | Independent case: naive footprint sum `89,859.744860 m²`, union `89,376.460900 m²`, reported `89,376.460900 m²`. |
| 22 | Priority draw/name/edit/delete/save/reopen | FAIL | Draw, name, delete, fresh save, and reopen pass; edit corrupts replacement geometry (P3-IR-01). |
| 23 | Pixel density stays null/not-calculated with no claim | PASS | Every result has `method=not-calculated`, `value=null`, `units=null`; code/UI scans found no analytics threshold or suitability claim. |
| 24 | Phase 4+ and proposed/automatic features gated | PASS | No corresponding engines/endpoints exist; rendered controls/layers remain disabled and explicitly labeled P4-P6. |

## 5. Contract, catalog, and migration review

### Frozen source material

- `Input/Miracle_Mile_Lighting_Poles.kml` SHA-256: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
- Every `Input/` file and all seven frozen Phase 1 catalog files are unchanged from `9f7f91f`.
- The engineering-data validator passed all seven schemas/catalogs, cross-references, reparsing, and supplied-source hashes.

### Additive contracts

- Project schema version is `2.2.0` and adds typed priority areas and camera geometry without removing Phase 1/2 fields.
- Fixture operational catalog version is `1.2.0`; it preserves r1 SMART templates and appends r2 fixed-zero-origin templates.
- Camera-equipment and IES operational catalogs remain `1.1.0`.
- The seven Phase 1 engineering catalogs remain `1.0.0`.
- Runtime and checked-in operational catalog schemas match exactly.
- Project/OpenAPI freshness fails only for the omitted priority-summary `warnings` field described in P3-IR-02.

### Independent migration preservation

For each source version `1.0.0`, `2.0.0`, and `2.1.0`, an independent payload included all imported source data, calculated/recommended legacy dictionaries, lighting/Wi-Fi configuration, and legacy camera relative-azimuth/downward-tilt bytes plus metadata. Migration to `2.2.0`:

- preserved the source layer exactly;
- preserved all existing pole edits and legacy override content exactly;
- preserved calculated and recommended legacy data exactly;
- added empty `priority_areas` and `camera_geometry` defaults; and
- validated under the runtime `Project` model.

## 6. Geometry and adversarial evidence

The independent lens calculation did not use the service's vertex function for its expected values. It separately formed boundary rays from the documented basis and calculated the projected polygon areas. All three results matched the service within `1e-6 m²`.

Adversarial direct cases returned these safe failures:

| Case | Result |
|---|---|
| Horizontal optical axis | No polygon; horizontal/upward/unstable warning |
| Upward tilt | No polygon; horizontal/upward/unstable warning |
| Exact horizontal boundary ray (`tilt=34°`, `V=68°`) | No polygon; horizontal/upward/unstable warning |
| NaN height | No polygon; non-finite input warning |
| Infinite origin | No polygon; non-finite input warning |
| 180-degree H FOV | No polygon; invalid input warning |
| Zero height | No polygon; invalid input warning |
| Micro-FOV degenerate polygon | No polygon; invalid/degenerate warning |

No case fabricated, clipped, or silently completed a polygon.

## 7. Rendered 74-pole workflow

The production frontend was built with an isolated API target and run at `http://127.0.0.1:3017/`; the isolated FastAPI service ran at `http://127.0.0.1:8017/`.

1. Imported the supplied KML: 74 source poles, LITE 74/WIFI 0/SMART 0, `EPSG:32617`, first coordinate exactly `-80.26234411,25.74920999,0`.
2. Assigned Cobra Head 7 to Phoenix 1 SMART template r2. Before height/lenses, both slots produced no polygon and clear missing-height/missing-lens warnings.
3. Set height 10 m, camera 1 JL-LN039, and camera 2 JL-LN042. Results were 290°/70°, 140° apart, with 241.6 m² and 1,147.0 m² footprints.
4. Changed fixture azimuth to 121.889°. Both footprints moved to 51.889°/191.889° and retained 140-degree separation.
5. Changed camera 1 to JL-LN037 and disabled camera 2. Camera 1 became 89,376.5 m²; camera 2 produced no polygon and no error.
6. Selected a second customer pole and assigned Solitaire SMART template r2 at 10 m with JL-LN039 on both slots. Results were 300°/60°, 120° apart.
7. With two SMART poles, the map showed three enabled valid footprints, two overlap pairs, and `483.3 m²` summed pairwise overlap.
8. Drew, named, saved, and summarized a valid priority area. The union coverage was displayed as `9,377.1 / 30,386.8 m² · 30.9%`.
9. Reproduced P3-IR-01 by editing that area. Deleted the invalid edited area successfully, then drew a fresh valid area for reopen verification.
10. Saved and reopened the project through visible controls. Reopen restored LITE 72/SMART 2, three valid footprints, two overlap pairs, priority geometry and summary, Phoenix/Solitaire fixture/template/camera/lens revisions, disabled state, warnings, and exact source coordinates.
11. Browser console warnings/errors: none.
12. Phase 4 Wi-Fi, Phase 5 photometry, Phase 6 CAP, reporting, and proposed/automatic-pole behavior remained unavailable.

## 8. Automated validation results

| Gate | Result |
|---|---|
| Complete backend suite | **PASS — 81 passed**; one existing Starlette/httpx2 deprecation warning |
| Engineering data/source integrity | **PASS** |
| Frontend rendered/workflow tests | **PASS — 5 passed** |
| Strict TypeScript | **PASS** |
| ESLint | **PASS** with zero errors/warnings |
| Production build | **PASS**; existing chunk-size and route-classification advisories |
| Operational catalog schema freshness | **PASS — 3 of 3** |
| Project schema freshness | **FAIL** |
| OpenAPI freshness | **FAIL** |
| `1.0.0`/`2.0.0`/`2.1.0` migrations | **PASS** |
| Exact all-pole source comparison after rendered save/reopen | **PASS — 74 of 74 complete tuples** |
| Independent lens calculations | **PASS — 3 of 3** |
| Independent invalid/unstable/degenerate cases | **PASS — 8 of 8 safe failures** |

The checked-in test suite does not detect P3-IR-01 or P3-IR-02: its priority-area test covers creation/reopen but not rendered replacement editing, and its generated-schema assertions cover the operational catalogs but not an exact project-schema/OpenAPI comparison.

## 9. Phase boundary

No Phase 4 Wi-Fi calculation, Phase 5 photometric engine, Phase 6 CAP recommendation, reporting engine, proposed-pole creation, pole optimization, or automatic placement implementation was found. Pixel density remains an explicit `not-calculated` seam with null value/units and no recognition, LPR, analytics, compliance, or suitability threshold.

This QA result does not authorize corrective implementation. Findings must be returned to an implementation session and independently retested. Phase 4 remains gated.

## 10. Final gate decision

**FAIL**

Phase 4 may not begin. At minimum, P3-IR-01 and P3-IR-02 require correction and independent retest. The Moderate and Minor findings should be resolved or explicitly dispositioned as part of the same Phase 3 corrective gate. No fixes were made in this QA session.
