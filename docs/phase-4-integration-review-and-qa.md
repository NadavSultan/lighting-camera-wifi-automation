# Phase 4 integration review and independent QA

Date: 2026-08-17

Role: independent Phase 4 QA engineer

Repository: `C:\Users\Nadav\Desktop\Automation Project\lighting-camera-wifi-automation`

## Overall result

**FAIL**

Phase 4 cannot be formally closed. Corrective implementation and a new independent retest are required. Phase 5 conceptual Wi-Fi must remain unauthorized and may not be considered for separate authorization while this Phase 4 gate is failed. This review neither authorizes nor begins Phase 5.

The gate fails because the application can present and persist stale lighting results after calculation-significant pole changes, can accept corrupt historical IES parsed metadata, accepts unsupported or discontinuous C-plane data, can persist non-finite calculations as null and make the project unreopenable, returns internal-server errors for permitted-but-unsafe spacing and invalid CRS input, and does not apply the approved boundary tolerance when enumerating lattice candidates.

## Review boundary and independence

- The implementation and completion reports were treated as unverified claims.
- Application code, schemas, catalogs, tests, governance documents, supplied inputs, and implementation reports were not modified.
- The only repository write made by this review is this report.
- All application runtime state used for rendered QA was isolated under temporary QA project/catalog directories outside the repository.
- No finding was fixed. Phase 5 or later implementation was not started.

## Baselines and repository integrity

The requested commit chain is exact and linear:

| Role | Commit | Parent | Subject |
|---|---|---|---|
| Governance baseline | `9ed85890503bd145dbc15f958fd6c6a770edcf52` | `b525091090b0f8435a6e6d7b1f0645a0304a8ef9` | `docs: restore lighting before Wi-Fi roadmap` |
| Phase 4 implementation | `eafd320369600ff4c8d32b8dc32c80e1e81b3d24` | `9ed8589...` | `feat: implement Phase 4 lighting calculation engine` |
| Phase 4 completion report | `9a7e5a4e84cdf8fdaf36af48e33f5799696d1280` | `eafd320...` | `docs: record Phase 4 implementation completion` |
| Pre-QA correction | `5ada5665ed26a85210da1ff1d4fa49d787cf276d` | `9a7e5a4...` | `fix: preserve historical IES revision pins` |
| Corrective completion report / tested HEAD | `cce899b4df5fc56f6380bfee79b3cec10193499c` | `5ada566...` | `docs: record Phase 4 pre-QA correction` |

The original Phase 4 completion report has Git blob `2c44e6096fdf19a8dc2aa33b4762e17419e56db3` at `9a7e5a4`, `5ada566`, `cce899b`, and HEAD. The corrective report has blob `60509a9d7dde7410c28607f8b86a892811a56eb0` at `cce899b` and HEAD. Both reports therefore correspond to the stated implementation parents and remained unchanged after their report commits.

The full `9ed8589..5ada566` implementation range changes 40 files with 2,538 insertions and 123 deletions. The changes are confined to Phase 4 contracts/services/UI/tests/documentation plus the additive IES history correction. No file under `Input/`, `data/fixtures`, `data/cameras`, `data/network`, or `data/luminaires` changed. `Input/` has the identical Git tree `7e39d2625dccfd5f72c936db5a1f87cafe61b2cd` at the governance baseline, corrective implementation, and HEAD.

Current supplied-source SHA-256 values independently matched the inventory, including:

- KML: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
- Phoenix 100 W: `4a897fb04b6d8f6c75c94a3ceba473391021aee6d506f05357f48bc01d26d363`.
- Phoenix 120 W: `eb05f9cc5064ab6a0fa19e2886ff0af9cecfa06a7f2ef0bc2e269e57929173c1`.
- Solitaire D01: `fda02adb7ca11c6ca5af8e930bdc5e1b8ffb5f558eb8a432a7d4fae87e18db38`.
- Solitaire D02: `4efa14cfe43e2214080bcd09d6424b353322010c07717106bc3218297839c86a`.

The engineering/source validator independently passed all seven frozen catalog/schema pairs and supplied-source hashes. No source pole, raw coordinate, embedded source byte, frozen Phase 1 catalog, or source-file tree changed. The diff contains no Wi-Fi coverage engine, CAP recommendation engine, reporting engine, proposed-pole workflow, optimization, or standards-compliance implementation. Phase 5 and later controls remained disabled in the production-rendered application.

There were no untracked files before this report. Ignored state consisted of expected virtual environments, dependency directories, Python/test caches, Vinext/Next/build output, TypeScript build state, temporary validation artifacts, and ignored runtime project/catalog data. Several prior QA/runtime projects existed under ignored `backend/data/` and `tmp/`; rendered QA therefore used isolated temporary stores so those files could not influence the result.

## Requirement-level results

| Review area | Result | Independent evidence |
|---|---|---|
| Scope and source integrity | Meets contract | Exact commit ancestry, full name/status and stats diffs, unchanged report blobs, unchanged `Input/` tree, current source hashes, validator, and rendered source checks. |
| Calculation-area separation and workflow | Partially meets | Four distinct lighting areas were created as ROAD, SIDEWALK, PARKING, and OTHER; priority areas remained a separate empty collection. Create/select/edit/empty redraw/cancel/invalid recovery/valid replacement/calculate/recalculate/save/reopen worked. Invalid maintenance factor preserved the existing result. Live rendered deletion was not executed; see unverified claims. P4-IR-07 affects invalid-draft labeling. |
| Stale-result safety | Does not meet | P4-IR-01. Pole height, active state, model, IES pin, and azimuth edit paths retain derived results until an explicit recalculation. |
| Deterministic projected grid | Partially meets | Projected-metre validation, origin anchoring, Y-then-X ordering, stable IDs, exact 25,000 acceptance, 25,001 rejection, no spacing enlargement, empty sets, zero sets, high latitude, and contribution threshold passed. P4-IR-05 and P4-IR-06 fail invalid-input and tolerance behavior. |
| Photometric equation and ordinary math | Partially meets | Independent derivation confirms `E_h = I cos(theta) / r^2 = I h / r^3`. Nadir, off-axis, inverse-square/incidence, summation, maintenance scaling, multiplier, exact samples, endpoints, single plane, 0-90 and 0-180 symmetry, normal full 0-360 seam, rotation sign, and fixed origin passed. P4-IR-03 and P4-IR-04 fail malformed-domain and finite-output behavior. |
| IES eligibility and compatibility | Meets ordinary-path contract | Exact supplied SHA restrictions cover Phoenix 1 LITE/WIFI/SMART and Solitaire LITE/WIFI/SMART. Cross-family association was rejected. There was no seed/default IES. Rendered upload preserved file identity and explicit association/selection. Invalid, malformed, unsupported, and non-`TILT=NONE` imports were blocked on ordinary cases. |
| Historical IES pins | Partially meets | Independent revision-1/revision-2 scenario retained 10 lx and revision-1 provenance through save/open/recalculate; explicit adoption alone moved to revision 2 and 20 lx; missing exact history returned 422 with no fallback. Lifecycle conflicts passed. P4-IR-02 shows corrupt parsed metadata is not rederived or rejected. |
| Solitaire decisions | Meets ordinary-path contract | Both supplied files parsed at 50 W while preserving the internal `60W` identifier. D02 retained raw dimensions `(-0.692, -0.692, 0.0)` and emitted global/per-result warnings stating that luminous-opening dimensions are excluded. |
| Results, statistics, persistence, provenance | Partially meets | A rendered result persisted/reopened 280 ordered points and later 19,319 points; independent recomputation matched average/minimum/maximum and both uniformity ratios. Point IDs/coordinates/plane/lux, fixture provenance, warnings, assumptions, disclaimer, source hashes, and authoritative coordinates persisted. P4-IR-01, P4-IR-02, and P4-IR-04 fail currentness, provenance integrity, and finite persistence. |
| Contribution threshold | Meets contract | An independent 20,001-point, five-fixture case produced a 100,005 product: every per-point contribution payload was omitted, totals/statistics remained exact, all five fixture provenance records remained, and the warning was present. |
| Contracts and migrations | Meets tested contract | Checked-in project schema, OpenAPI, and IES schema exactly equaled fresh in-memory generation. Versions were project `2.4.0`, software/API `0.4.0`, and IES `1.2.0`. All five migrations preserved source, edits, exact IES pins, camera geometry, priority data, legacy calculated/recommended data, and quarantine data while starting Phase 4 collections empty. |
| Production-rendered application | Partially meets | Imported all 74 poles; uploaded Phoenix 100 W and Solitaire D02; created all six allowed representative associations; configured 40 SMART, 10 WIFI, and 14 Solitaire LITE poles; produced 80 valid camera footprints; exercised four lighting classifications, invalid redraw recovery, settings validation, calculation/recalculation, rotation, layers, warnings, save/reopen, and a 19,319-point result. Console errors/warnings were empty and all observed local API requests were 2xx. P4-IR-01 was reproduced visibly. |
| Phase 1-3 regression | Meets tested contract | Complete backend suite and focused Phase 2/3 suites passed; rendered source coordinate and Phase 3 fixed camera behavior remained intact. No Phase 1-3 regression was confirmed. |
| Claims and limitations | Meets labeling contract | AGi32/professional-reference absence was visible and persisted. No compliance, equivalence, suitability, target recommendation, or professional-grade claim was found. All approved physical/model exclusions remained explicit. |

## Confirmed defects

### P4-IR-01 — Critical — Calculation-significant pole edits leave stale lighting results presented and persisted as current

- **Affected files/components:** `frontend/app/components/EngineeringWorkspace.tsx` (`updatePole`, `restorePole`, `applyBulkConfiguration`, fixture assignment/edit callbacks); `backend/app/main.py` save/open/bulk paths; persisted `lighting_calculations.results`.
- **Reproduction steps:** Import the supplied 74-pole KML. Upload and explicitly associate/select Phoenix and Solitaire IES files. Configure fixtures, draw an area, and calculate it. Change a contributing pole height from 10 m to 20 m in the rendered inspector, or bulk-change contributing fixture azimuth/model/IES/height. Observe the lighting row before recalculation. Save and reopen the project JSON.
- **Expected behavior:** Every change affecting calculation meaning must remove the affected result or clearly mark it stale before it can be displayed or persisted as current.
- **Actual behavior:** The rendered row continued to display `280 points · Eavg 5.83 lx · Emin 0.00 lx · Emax 97.66 lx` immediately after the height changed to 20 m, after Save Project, and after rendered reopen. Persisted fixture provenance still said height 10 m. A separate API reproduction produced `edit_height_after_save=20`, `persisted_result_height=10`, `persisted_center_lux=10`, `result_equal_before_after=True`, and `reopen_result_equal=True`. Bulk rotation likewise left `5.83/0.00/97.66` displayed until recalculation, after which the valid result changed to `5.72/0.00/79.87`.
- **Evidence:** `EngineeringWorkspace.tsx` only deletes an area result inside the area-edit and area-delete paths. Pole update, restore, per-pole configuration, and bulk configuration paths do not invalidate lighting results. Backend save/open/bulk validation also preserves supplied result objects without comparing their inputs or provenance to current configuration.
- **Phase-gate impact:** Gate-failing. An engineer can be shown and can reopen numerically obsolete lighting results without a stale warning.

### P4-IR-02 — Major — Historical IES resolver accepts parsed metadata that contradicts immutable bytes

- **Affected files/components:** `backend/app/catalog_models.py` (`IesFileRecord.validate_original_content`); `backend/app/services/ies.py` (`resolve_pinned_ies_revision`); `backend/app/services/lighting_calculation.py` fixture provenance.
- **Reproduction steps:** Create valid revision-1 bytes for a 50 W, 1,000 cd Type C file. Preserve its valid Base64 and SHA but alter `parsed_metadata.input_watts` to `999`. Put that record in `file_history`, make revision 2 current, and resolve/calculate the revision-1 pin.
- **Expected behavior:** A corrupt historical pin whose parsed metadata does not exactly match re-parsing of its immutable bytes must fail clearly with no fallback or false provenance.
- **Actual behavior:** The resolver accepted revision 1. Re-parsing the bytes returned 50 W, while persisted result provenance reported 999 W. The numerical center result was 10 lx because calculation used the bytes, leaving numerical output and claimed parsed provenance internally contradictory.
- **Evidence:** The resolver reconstructs the existing model, which rechecks Base64 and SHA, but never re-runs the IES parser or compares parsed metadata with parsed bytes. Lighting provenance copies `record.parsed_metadata` directly.
- **Phase-gate impact:** Gate-failing. Exact historical provenance is a mandatory Phase 4 contract and cannot be trusted under catalog corruption.

### P4-IR-03 — Major — Unsupported C-plane domains and discontinuous 0/360 endpoints are accepted as valid

- **Affected files/components:** `backend/app/services/ies.py` IES semantic validation; `backend/app/services/lighting_calculation.py` `_canonical_c_angle` and `interpolate_candela`.
- **Reproduction steps:** Import a strictly increasing Type C file with horizontal planes `[10, 20]`; then evaluate C0, C15, and C180. Separately import a `[0, 180, 360]` file whose C0 row is 100 cd and C360 row is 900 cd; evaluate C0, C359.999, and C360.
- **Expected behavior:** Only the approved single-plane, 0-90 symmetry, 0-180 symmetry, or complete 0-360 domains should calculate. Unsupported partial domains and inconsistent duplicated seam endpoints should be rejected as invalid/malformed.
- **Actual behavior:** `[10, 20]` was marked valid and returned 0 cd at C0/C180 while returning 150 cd at C15. The inconsistent full-seam file was marked valid and returned 100 cd at C0, approximately 899.996 cd at C359.999, then 100 cd at C360, producing a discontinuity at the declared seam.
- **Evidence:** The parser checks only strict increase and numeric bounds; it does not require an approved horizontal domain or seam consistency. The interpolator returns zero outside the unsupported partial range and independently uses both 0 and 360 rows.
- **Phase-gate impact:** Gate-failing. Validated inputs can produce silently fabricated zero regions or a discontinuous azimuth distribution.

### P4-IR-04 — Critical — Finite source values can overflow to non-finite lux, serialize as null, and make the saved project unreopenable

- **Affected files/components:** `backend/app/services/ies.py` numeric magnitude validation; `backend/app/services/lighting_calculation.py` candela multiplication, illuminance, summation, and result construction; `backend/app/models.py` finite result validation; `backend/app/services/store.py` JSON persistence.
- **Reproduction steps:** Import a syntactically valid Type C file whose finite candela values and finite positive multiplier are both `1e308`. Calculate a normal 10 m nadir area through the API, then reopen the saved project.
- **Expected behavior:** Unsafe magnitudes must be rejected at import or calculation with a clear 4xx response; no non-finite value or corrupted project may be persisted.
- **Actual behavior:** The record was marked valid. Direct illuminance was `inf`, and the result model accepted `inf`. The API returned 200 but serialized affected lux values as JSON `null`; the store persisted null values. Subsequent project load failed model validation and the GET endpoint returned 404 `Project not found`, masking the corrupt persisted project as absence.
- **Evidence:** Input values are checked for finiteness individually but products/sums are not. `StrictModel` does not forbid `inf`/`nan`, result fields only specify `ge=0`, and persistence serializes the non-finite model to null.
- **Phase-gate impact:** Gate-failing and data-integrity critical. A calculation-eligible upload can make a stored project unavailable.

### P4-IR-05 — Major — Invalid CRS and subnormal positive spacing escape controlled validation and return HTTP 500

- **Affected files/components:** `backend/app/models.py` `CalculationArea.grid_spacing_m`; `backend/app/services/lighting_calculation.py` CRS construction and lattice index calculation; `backend/app/main.py` calculation exception handling.
- **Reproduction steps:** Submit a valid project/area with `projected_crs="NOT-A-CRS"` and calculate. Separately use `EPSG:32617` with finite positive spacing `5e-324` and calculate.
- **Expected behavior:** Invalid/unsupported CRS and unsafe spacing must be rejected as readable validation errors, must not crash, and must preserve any prior valid result.
- **Actual behavior:** Both requests returned HTTP 500 `Internal Server Error`. The invalid CRS raises `pyproj.exceptions.CRSError`, while subnormal spacing overflows `min_x / spacing` and raises `OverflowError: cannot convert float infinity to integer`; the endpoint catches only `ValueError`.
- **Evidence:** The model enforces only `grid_spacing_m > 0` and `<= 1000`, with no safe lower bound. `CRS.from_user_input` and `math.ceil/floor` are executed before a controlled exception conversion.
- **Phase-gate impact:** Gate-failing. Required invalid/unsupported input handling is not safe or deterministic.

### P4-IR-06 — Major — Boundary-tolerance points outside the raw polygon bounds are never enumerated

- **Affected files/components:** `backend/app/services/lighting_calculation.py` `deterministic_grid`.
- **Reproduction steps:** Use spacing 1 m and a rectangle whose minimum X edge is `9.99e-8 m` east of lattice point `(0,0)`, while Y spans `-1` to `1`. Generate the grid and test membership of `(0,0)`. Repeat at `1.001e-7 m`.
- **Expected behavior:** `(0,0)` is within the approved `1e-7 m` boundary tolerance in the first case and must be accepted; it must be rejected in the second case.
- **Actual behavior:** `(0,0)` was rejected in both cases. Exact-boundary `0` was accepted. The same failure occurred around a vertex.
- **Evidence:** Candidate indices use `ceil(min_x / spacing)` and `floor(max_x / spacing)` from the unbuffered polygon bounds. The later `polygon.buffer(1e-7).covers(...)` test cannot accept a nearby lattice point that was never enumerated.
- **Phase-gate impact:** Gate-failing. The implemented point set contradicts the exact approved tolerance contract and may omit points after coordinate transformation noise.

### P4-IR-07 — Minor — Calculation-area validation errors are mislabeled as priority-area errors

- **Affected files/components:** `frontend/app/lib/phase4-workflows.mjs`; `frontend/app/lib/phase3-workflows.mjs`; rendered calculation-area editor.
- **Reproduction steps:** Start Redraw on a lighting calculation area, add fewer than three distinct vertices, and select Validate and save polygon.
- **Expected behavior:** The rendered error should identify the invalid lighting calculation area/draft.
- **Actual behavior:** The UI displayed `A priority area requires at least three distinct vertices.` Similar self-intersection/degeneracy messages also say priority area because the Phase 4 helper calls the Phase 3 priority-ring validator directly.
- **Evidence:** `phase4-workflows.mjs` imports and returns `validateAndClosePriorityRing`; that helper hard-codes priority-area wording. The prior valid calculation polygon remained stored, so the defect is labeling rather than data loss.
- **Phase-gate impact:** Does not fail the gate alone, but contradicts the required structural/behavioral separation in user-facing recovery messaging.

## Regressions

No Phase 1, Phase 2, or Phase 3 regression was confirmed.

- The complete backend suite passed 101 tests.
- The focused Phase 2 catalog/revision plus Phase 4 suite passed 44 tests.
- The complete Phase 3 geometry/regression suite passed 34 tests.
- The rendered project retained all 74 poles, the first pole ID `pole-443127e3a723e1b3`, raw coordinate `-80.26234411,25.74920999,0`, longitude `-80.26234411`, and latitude `25.74920999`.
- Forty configured Phoenix SMART poles produced 80 valid fixed-mount footprints. Camera/lens pins, fixed `-70/+70` relative azimuths, fixed 35-degree downward tilt, and zero XYZ origins remained visible.
- The embedded and archived KML bytes remained identical to the supplied KML hash.

## Historical revision-pin adversarial retest

The ordinary historical-pin correction works for internally consistent records:

- Revision 1 used known 1,000 cd bytes, SHA `a8cee902346db99d1363ae87248bf8fcf303f39a7b3a691102a9554072f524d8`, filename `qa-revision-1.ies`, warning `qa-r1-warning`, and produced exactly 10 lx at 10 m nadir.
- Revision 2 used different 2,000 cd bytes, SHA `4d38fecaa49f5ab28e4c91306de3e9a1d55f4f5d50ecb76ea97883728a9cdf55`, filename `qa-revision-2.ies`, warning `qa-r2-warning`, and was current while the project remained pinned to revision 1.
- Ordinary save, GET/open, and recalculation all retained pin 1 and identical ordered point values.
- Explicit bulk reselection alone adopted revision 2; the next result contained revision-2 identity and produced exactly 20 lx.
- Removing revision 1 from history caused HTTP 422: `selected IES revision 1 is missing; current revision was not substituted`.
- Duplicate revision keys and checksum/Base64 corruption are rejected by model validation; inactive/invalid/unsupported current or pinned records and missing/inactive associations are rejected; referenced lifecycle operations return conflicts.

P4-IR-02 prevents this section from passing the mandatory corrupt-pin requirement as a whole because parsed metadata corruption remains accepted.

## Rendered application evidence

The actual production Vinext build was served against the FastAPI application with isolated storage and exercised through the rendered interface.

- Imported `Input/Miracle_Mile_Lighting_Poles.kml`: 74 source poles, five folders, `EPSG:32617`.
- Uploaded Phoenix 100 W and Solitaire D02 through the real file chooser. Rendered catalog records showed valid revision 1, the expected SHA prefixes, and D02's negative-dimension warning.
- Explicitly associated Phoenix to Phoenix 1 LITE/WIFI/SMART and Solitaire to Solitaire LITE/WIFI/SMART. No default was set.
- Configured Cobra Head (40) as Phoenix SMART at 10 m with explicit IMX477/JL-LN039 pins, Other (14) as Solitaire LITE at 9 m, and Decorative (10) as Phoenix WIFI at 8 m. This produced rendered counts LITE 24, WIFI 10, SMART 40 and 80 valid camera footprints.
- Created four separate lighting areas: `QA Road`/ROAD, `QA Sidewalk`/SIDEWALK, `QA Parking`/PARKING, and `QA Other`/OTHER. Camera `priority_areas` remained empty and visually separate.
- Invalid redraw preserved the prior polygon; invalid maintenance factor 1.1 preserved the prior result; valid rename/settings edit removed the prior result; valid redraw replaced geometry and recalculated.
- Initial road calculation produced 280 points and 64 contributors. Full-precision persisted statistics independently recomputed exactly from persisted point values.
- Rendered height and bulk-azimuth edits reproduced P4-IR-01. Explicit recalculation after rotating all Phoenix fixtures changed Eavg/Emax from 5.83/97.66 lx to 5.72/79.87 lx, while fixed source origins remained unchanged.
- Save/reopen restored the corrected recalculated result and all 74 poles. Full fixture/IES revision, SHA, filename, parsed metadata, height, azimuth, origin, CRS, grid policy, model version, assumptions, warnings, and disclaimer were visible/persisted on ordinary data.
- A 19,319-point, 64-contributor result completed and rendered without console error; contribution payloads were omitted as designed while totals/provenance remained.
- Calculation Areas, Calculation Points, and Lighting Results controls/layers were distinct from camera FOV, overlap, Priority areas, and Warnings. Conceptual Wi-Fi P5 and CAP P6 remained disabled.
- Browser console errors and warnings were empty. Every observed API request in server access logs completed with 2xx during this ordinary rendered workflow.

## Generated contracts and migration evidence

Fresh canonical in-memory comparisons were exact:

| Artifact | Equality | Canonical generated SHA-256 |
|---|---:|---|
| `schemas/project.schema.json` | exact | `858d1c7d1c908bf5d582b1696e523dcdfeb37f9cca6562ef50e41f46afac46ed` |
| `schemas/openapi.json` | exact | `c9506ab6339ec15013cbadb08ae07588f493004ff1bf67ab463e3ed8e0affd11` |
| `schemas/ies-library.schema.json` | exact | `6a423633928dc710d836bf40a59b7a949e4052b37ee5d54dbd59cf14f8a9109c` |

All three artifacts were independently compared for exact object equality. Project/software/API/IES versions were `2.4.0`, `0.4.0`, `0.4.0`, and `1.2.0` respectively.

An independent five-version migration matrix used a populated 74-pole project with exact IES pins, 80 camera footprints, priority data, arbitrary legacy calculated/recommended payloads, and quarantine data. Versions `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, and `2.3.0` all validated as `2.4.0`, preserved those collections byte/value-for-value, retained IES revision 1 and source SHA, and created empty `calculation_areas`/`lighting_calculations`. No calculation area, fixture family, IES mapping, or default was inferred.

## Regression and validation commands

| Validation | Outcome |
|---|---|
| Complete backend suite: `python -m pytest -p no:cacheprovider` | 101 passed; one existing Starlette/httpx2 deprecation warning |
| Focused Phase 2 + Phase 4: `test_phase2_catalogs.py test_phase4_lighting_calculation.py` | 44 passed; same deprecation warning |
| Complete Phase 3: `test_phase3_camera_geometry.py` | 34 passed |
| Engineering/source validator | Passed seven catalog/schema pairs and all source hashes/invariants |
| Frontend rendered/workflow tests with pinned Node | 7 passed |
| Strict TypeScript with pinned Node | Passed |
| ESLint invoked directly with pinned Node | Passed with zero warnings/errors |
| Production Vinext build invoked directly with pinned Node | Passed |
| Exact in-memory contract comparison | Passed all three required artifacts |
| All five supported migrations | Passed preservation checks |

The green checked-in suites do not cover P4-IR-01 through P4-IR-06 and therefore do not override the independent reproductions.

## Accepted limitations

The following are disclosed, persist in results where applicable, and are accepted Phase 4 MVP limitations rather than defects:

- No AGi32 or other professional-reference comparison exists. Every result states that it is not independently validated against such a tool.
- The engine makes no equivalence, compliance, suitability, target recommendation, or professional-grade claim.
- Zero physical luminaire tilt and C0-to-fixture-azimuth alignment are approved MVP assumptions; `TILT=NONE` is not treated as proof of installed zero tilt.
- Terrain, slope, obstruction, buildings, occlusion, shadow, reflected light, interreflection, atmosphere, near-field luminous-opening geometry, and depreciation beyond explicit maintenance factor remain excluded.
- Point result coloring is not an independently validated isolux/contour engine.
- Per-fixture point contributions may be omitted above the 100,000 point-by-contributor threshold while totals and complete fixture provenance remain.

None of these accepted limitations excuses the contradictory behavior in the confirmed defects.

## Advisory observations and toolchain findings

- A rendered 19,319-point calculation with 64 contributors kept the application busy for roughly 80 seconds before the UI restored interaction and rendered the result. It completed without console/network error and no contractual latency target exists, so this is recorded as a performance advisory rather than a confirmed defect. It should be included in corrective performance regression because it is representative of the supported point range.
- Pytest emits the existing non-failing Starlette `TestClient`/future-httpx2 deprecation warning.
- The production build emits the existing non-failing MapLibre chunk-size advisory and Vinext route-classification advisory.
- The dependency-refreshing pnpm wrapper aborted under non-TTY with `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`. Direct pinned Node invocations of tests, TypeScript, ESLint, and Vinext succeeded.
- `git diff --check 9ed8589..5ada566` reports two intentional Markdown hard-break pairs in the Phase 4 completion report and a genuine extra blank line at EOF in `frontend/app/lib/phase4-workflows.mjs`. The corrective implementation diff itself is clean. The corrective completion-report commit similarly uses two intentional Markdown hard breaks.

## Unverified claims caused by an environmental blocker

- A destructive live-browser click on Delete was not executed against even the isolated temporary rendered project because the browser safety boundary requires separate action-time confirmation for deletion. The deletion implementation was inspected: it removes only the selected calculation area and its same-ID derived result while leaving source poles and camera priority areas untouched. This is source evidence, not rendered deletion proof, and must be included in corrective retest.
- No AGi32/professional-reference comparison environment or reference model was supplied. Its absence is correctly disclosed and is an accepted limitation, not evidence of numerical equivalence.

## Final gate statement

- **Phase 4 can be formally closed:** No.
- **Corrective implementation and independent retest are required:** Yes, for P4-IR-01 through P4-IR-06; P4-IR-07 should be corrected in the same bounded Phase 4 correction.
- **Phase 5 may be considered for separate authorization now:** No. It may be considered only after Phase 4 receives a later independent passing gate. This report does not authorize or begin Phase 5.
