# Phase 2 Corrective Integration Retest and QA Report

**Review date:** 2026-08-15  
**Review type:** Independent corrective integration review and QA retest  
**Corrective implementation:** `081da6ed9aa52a792112d3a1ed9b6c7e69a5d006`  
**Corrective completion report:** `5a4531268a66eaf414073f60189f1356b9246fe5`  
**Original QA report:** `docs/phase-2-integration-review-and-qa.md`  
**Final gate:** **PASS WITH CONDITIONS**

## 1. Executive conclusion

The Phase 2 corrective implementation resolves the safety, data-integrity, contract, migration, and workflow defects recorded as IR-01 through IR-11. All eleven original findings are closed for corrective acceptance. The historical fact behind IR-11 remains explicitly preserved rather than backdated; the new retrospective ratification is sufficient for the corrective gate because it acknowledges the original process failure and records the later authorization and accepted contract.

One new low-severity frontend feedback defect was found. A rejected IES upload is correctly persisted as an inactive invalid/unsupported record, but the already-open catalog dialog does not refresh that record immediately and renders the structured 422 detail as raw JSON. Reloading the application displays the retained record, its readable validation error, its disabled activation control, and an association list that excludes it. This does not compromise persistence, lifecycle restrictions, project validity, source data, or later-phase gating.

The condition for an unconditional PASS is to refresh the IES catalog from the retained 422 record (or refetch it) and present a concise validation message immediately after a failed upload. This is a Phase 2 UI follow-up only. It does not authorize Phase 3.

## 2. Scope and independence

The review began with a read-only audit of repository guidance, the original QA report, corrective completion report, commit graph, corrective diff, contracts, migrations, schemas, backend implementation, frontend implementation, seed data, and tests. The corrective completion report was treated as a claim set, not as test evidence.

Independent adversarial tests were then run against isolated temporary catalog and project stores. The rendered frontend was exercised against a current corrective development build and an isolated API/store. No implementation fix was made during QA, and no Phase 3 or later functionality was started.

The original QA report remained byte-for-byte unchanged. Its SHA-256 before and after retest was:

`FB6A391D2623ED9F8E547CC20516793354EDAA0476746BE3D412F3E94234AC03`

## 3. Commit and change-set verification

| Item | Result | Evidence |
|---|---|---|
| Corrective implementation identity | PASS | `081da6e` is a child of Phase 2 commit `40aee26` and is titled `fix: complete Phase 2 corrective QA work`. |
| Completion-report identity | PASS | `5a45312` is a direct child of `081da6e` and is titled `docs: add Phase 2 corrective completion report`. |
| Completion-report scope | PASS WITH NOTE | Besides the report, the commit adds one traceability sentence to `docs/current-status.md`; it does not change application code or contracts. |
| Original report preservation | PASS | The original report remained untracked and its recorded SHA-256 did not change. |
| Later-phase exclusion | PASS | No FOV projection, Wi-Fi coverage analysis, illuminance engine, CAP recommendation, proposed-pole generation, or automatic pole-placement implementation was found. Later-phase controls remain disabled and labeled P3-P6. |

## 4. Disposition of original findings

| Finding | Original severity | Retest disposition | Independent evidence |
|---|---:|---|---|
| IR-01 — Catalog revisions overwrite history | Major | **CLOSED** | Independently updated fixture, camera, and lens records. Each current record advanced to revision 2 while the complete revision-1 record remained addressable in the appropriate history collection. A project pinned to fixture/template/camera/lens revision 1 remained valid after all three catalogs advanced. New assignments carried exact equipment revision pins. |
| IR-02 — Referenced camera deactivation can cause HTTP 500 | Major | **CLOSED** | Referenced camera and fixture deactivation returned HTTP 409 with project/pole/slot references. A project exposed to an administratively inactive camera returned HTTP 422 rather than 500. The rendered catalog workflow also displayed readable referenced-record conflicts. |
| IR-03 — IES validation accepts invalid candela content | Major | **CLOSED** | Independent mutations with negative and non-finite candela values were rejected. Checked-in coverage additionally exercises unordered angles. Parser review confirmed finite-number, header/count, angle range/order, photometric type/unit, and exact candela-count checks. |
| IR-04 — IES warning/error contract is incomplete | Major | **CLOSED WITH LOW-SEVERITY FOLLOW-UP** | Invalid/unsupported uploads return 422 and are retained inactive with `validation_errors`; valid records support `validation_warnings`; frontend types and persisted-row rendering expose both. All generated schemas declare Draft 2020-12 and match runtime generation. NIR-01 records the immediate-dialog refresh/formatting defect. |
| IR-05 — Inactive IES records can become defaults | Major | **CLOSED** | Invalid association, default selection, and reactivation attempts each returned HTTP 422. Inactive/invalid records are absent from the rendered active-valid association selector, and activation/default controls are disabled or blocked. Deactivation cleanup is covered by the full backend suite. |
| IR-06 — Camera/lens compatibility can become asymmetric | Major | **CLOSED** | Lens `compatible_camera_model_ids` is authoritative; the camera-side list matched its exact derived reciprocal set. Contract validation rejected asymmetric payloads, and the rendered lens selector used the authoritative lens relation. |
| IR-07 — Domain-inconsistent project payloads are accepted | Major | **CLOSED** | Changing only `fixture_type` from SMART to LITE on a Phoenix 1 SMART configuration returned HTTP 422 with the classification-conflict diagnostic. |
| IR-08 — Manual multi-pole bulk selection is absent | Major | **CLOSED** | In the current rendered build, `Cobra Head 7` and noncontiguous `Lighting and Camera 32` were selected from the map into a two-pole manual set. Applying Phoenix 1 SMART changed exactly two poles: LITE 74→72 and SMART 0→2. |
| IR-09 — Empty bulk height erases data | Major | **CLOSED** | A bulk payload explicitly supplying null for height, azimuth, Wi-Fi configuration, and lens mapping returned 200 and left the existing 9.25 m height and unrelated configuration unchanged. All source coordinates remained exact. |
| IR-10 — Individual overrides cannot be removed | Major | **CLOSED** | In the current rendered build, assigning `JL-LN039` to camera-1 produced one pole override and its removal control. Removing it deleted only that slot delta, restored `Unassigned` from the catalog template, removed the control, and left both slots labeled `Catalog default`. |
| IR-11 — Missing approval provenance | Major | **CLOSED FOR CORRECTIVE ACCEPTANCE** | `phase-2-contract-ratification.md` explicitly calls itself retrospective and states that it does not backdate approval or alter the original QA report. `decision-log.md` states that it does not claim the original gate was met or weaken IR-11. The ratified versions, authority decisions, migration policy, risk entry, and later authorization are now reviewable. The original historical process failure remains factual. |

## 5. Automated validation matrix

| Suite | Command or method | Result |
|---|---|---|
| Full backend | `..\.venv\Scripts\python.exe -m pytest -ra` from `backend` | **PASS — 51 passed**; one non-failing Starlette/httpx deprecation warning. |
| Engineering data and source integrity | `.\.venv\Scripts\python.exe .\scripts\validate_engineering_data.py` | **PASS** — seven Phase 1 catalogs, schemas, traceability, units, camera bounds, IES parsing/references/hashes, CAP unknowns, calculation-area rules, and all supplied-source hashes. |
| Frontend workflow tests | pinned Node runtime with `--test tests/rendered-html.test.mjs` | **PASS — 3 passed**. |
| TypeScript | pinned Node runtime running `tsc --noEmit` | **PASS**. |
| ESLint | pinned Node runtime running ESLint with generated-output exclusions | **PASS**. |
| Production build | pinned runtime `pnpm run build` | **PASS**. The existing non-failing >500 kB chunk advisory remains. |
| Schema freshness | Independent in-memory generation comparison | **PASS** — `project.schema.json`, `openapi.json`, and all three Phase 2 operational schemas exactly match current runtime generation. |
| Draft declaration/schema validity | `Draft202012Validator.check_schema` plus declaration checks | **PASS** — project and all three operational schemas explicitly declare `https://json-schema.org/draft/2020-12/schema`. |
| Project migrations | Full suite plus independent 2.0.0 migration and unsupported-version probes | **PASS** — 1.0.0 and 2.0.0 migration paths pass; 0.9.0, 1.5.0, and 3.0.0 reject. |
| Operational catalog migration | Full backend migration coverage | **PASS** — initial 1.0.0 operational catalogs load as 1.1.0 with history collections and revision-1 template equipment pins. |
| Coordinate preservation | Full KML/project/bulk suite plus independent all-pole tuple comparison | **PASS** — ID, raw coordinate text, longitude, and latitude remained exact for every imported pole. |

## 6. Independent adversarial retest details

The independent test did not import implementation test helpers. It created new isolated stores, imported the supplied 74-pole KML through the API, and exercised public APIs plus runtime models.

Key results:

- The embedded source SHA-256 exactly matched the supplied KML bytes.
- SMART assignments carried `(fixture revision, template revision, camera revision, lens revision) = (1, 1, 1, 1)`.
- Updating fixture, camera, and lens records retained complete revision-1 snapshots and advanced current revisions.
- The revision-1 project remained valid after current catalog records advanced.
- Referenced camera deactivation returned 409; inconsistent project classification returned 422.
- Explicit-null bulk fields left height and nested values unchanged.
- Every source tuple `(id, raw_coordinates, longitude, latitude)` remained identical through bulk operations and migration.
- Negative and NaN candela payloads were rejected with retained inactive records and specific errors.
- Unsupported upload, invalid association, invalid default, and invalid activation returned 422.
- Camera/lens reciprocal lists exactly matched the authoritative lens relation.
- All five generated contracts were fresh.
- Initial Phase 2 migration preserved exact source coordinates, and unsupported schema versions rejected.

## 7. Rendered frontend retest

The current corrective frontend was run at `http://localhost:3001/` against an isolated FastAPI instance. The rendered UI imported `Miracle_Mile_Lighting_Poles.kml`, reported 74 authoritative source poles, and displayed the first raw coordinate exactly as `-80.26234411,25.74920999,0`.

The following workflows were executed through visible controls:

1. Selected manual targeting.
2. Added the initially selected `Cobra Head 7`.
3. Clicked a separate map marker and selected `Lighting and Camera 32` at raw coordinate `-80.2551142126106,25.7498784611578,0`.
4. Applied Phoenix 1 SMART only to the two-pole manual set and observed LITE 72 / SMART 2.
5. Added a lens override to camera-1 and removed only that slot override, restoring catalog defaults.
6. Saved a SMART project, attempted fixture and camera deactivation, and observed explicit referenced-record conflict messages rather than a crash.
7. Uploaded an unsupported IES, reloaded, and observed the retained error, disabled activation, active-valid-only selector, and disabled association/default actions.
8. Confirmed Draw Calculation Area, Calculate Lighting, Recommend CAP, FOV, Wi-Fi coverage, calculation, and CAP layers remain disabled/gated.

No browser console error or warning was emitted during the current-build workflow.

## 8. New findings

### NIR-01 — Low — Failed IES upload does not refresh the open catalog dialog

Reproduction:

1. Open the Phase 2 catalog manager.
2. Upload a file that is not supported LM-63 content.
3. Observe the catalog dialog before reloading.

Expected: the retained invalid/unsupported record appears immediately with a concise validation message and disabled lifecycle/association controls.

Actual: the API correctly returns 422 and persists the record, but the open dialog continues to show `No operational IES files uploaded`, while the global error surface displays the full structured response as raw JSON. After reload, the record and its validation error render correctly, activation is disabled, the association selector contains only its placeholder, and association/default actions are disabled.

Severity rationale: low. This is stale feedback and poor error formatting, not a persistence or safety failure. The retained record, validation diagnostics, lifecycle restrictions, schema contract, and API responses are correct.

Required condition: update the failed-upload UI path to consume the returned retained record or refetch catalogs and present the server message in human-readable form. Retest that single workflow before calling the gate an unconditional PASS.

No new Critical, Major, or Moderate findings were identified.

## 9. Phase 1 regression and later-phase boundary

Phase 1 import, validation, project persistence, KML coordinate fidelity, embedded source identity, and edit-overlay separation remain intact. The seven Phase 1 engineering data catalogs remain at their approved `1.0.0` contracts and pass source-hash validation.

Known engineering limitations remain explicit: authoritative fixture/IES applicability, Solitaire wattage resolution, physical camera offsets, approved default lens assignments, and terrain/ground assumptions are not invented. Those inputs continue to block dependent later work.

Phase 3 is not authorized by this result. Camera ground projection/FOV, Wi-Fi coverage, lighting calculation, CAP recommendation, and proposed/automatic pole workflows remain excluded.

## 10. Final gate decision

**PASS WITH CONDITIONS**

The original eleven Major findings are corrected sufficiently to close the Phase 2 corrective gate. The only condition is the low-severity immediate failed-IES-upload feedback defect NIR-01. Phase 2 may be treated as technically accepted with that follow-up tracked, but Phase 3 must not begin without a separate explicit authorization and its required engineering inputs.
