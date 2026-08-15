# Phase 2 Integration Review & QA Report

Review date: 2026-08-14

Project: Lighting Camera WiFi Automation

Scope: Phase 2 — Fixture, IES, and Camera Catalogs

Review type: Independent integration review and QA

## 1. Executive summary

Phase 2 does not pass its independent acceptance gate. The implementation contains no confirmed Blocker or Critical defect, but multiple Major defects violate required catalog-revision, IES-validation, inactive-reference, per-pole override, bulk-selection, and API-consistency behavior. Phase 3 must not begin.

The implementation correctly preserves the seven Phase 1 engineering catalogs, upgrades projects to schema `2.0.0`, migrates Phase 1 data without inferring Phoenix 1 or Solitaire, provides all six required fixture models, implements the approved Phoenix and Solitaire SMART mounting geometry, preserves source coordinates, passes the checked-in automated suite, and exposes the primary Phase 2 workflows in the rendered UI.

However, camera, lens, and general fixture catalog edits overwrite prior record content instead of retaining immutable revisions; referenced camera deactivation can cause project validation to return HTTP 500; the IES parser accepts semantically invalid candela data; inactive IES records can be restored as defaults through inconsistent association state; individual pole overrides cannot be removed in the UI; manual multi-pole bulk selection is absent; and API payloads can create classification/configuration mismatches or erase height through explicit `null`.

The Git history also does not contain an independently approved pre-implementation Phase 2 contract and migration proposal. The three operational contracts, migration assertion, and approval wording first appear in the Phase 2 implementation commit itself and therefore require explicit retrospective ratification.

## 2. Final result

**FAIL**

Phase 3 may not begin. Major defects remain in required Phase 2 behavior, and missing physical camera offsets, lens selections, and terrain assumptions independently block Phase 3 ground-FOV geometry.

## 3. Review basis and Phase 2 understanding

Phase 2 is expected to provide:

- Six structured Phoenix 1 and Solitaire fixture models with capability-driven behavior.
- Operational fixture-model, IES, and camera/lens catalogs separate from the seven frozen Phase 1 engineering catalogs.
- Immutable, revision-pinned SMART mounting templates.
- Validated and immutable IES uploads with explicit many-to-many fixture associations and one selectable default per fixture.
- Separately managed, versioned camera and lens records with explicit compatibility.
- Safe per-pole and explicit-field bulk configuration.
- Lossless Phase 1 migration without family inference or coordinate changes.
- A complete rendered frontend workflow while keeping Phase 3 and later engines gated.

The review covered repository guidance, planning and status documents, Phase 1 completion and validation reports, schema contracts, Phase 2 completion claims, architecture and data-model documentation, engineering conventions and open questions, Git history, contracts, seed data, generated schemas/OpenAPI, backend implementation, frontend types and behavior, persistence, automated tests, production build, adversarial API checks, and a live rendered workflow.

Relevant history:

- `c7751b0` — Finalize engineering schema contracts.
- `39495cfb6d6ab9b419f79cc66a7094854b0ccd55` — Complete Phase 2 fixture IES and camera catalogs.
- `40aee26cebb293dea01bc992d55200bd73357bb2` — Record Phase 2 implementation commit in the completion report.

The worktree was clean before and after the read-only audit. This report is the only approved repository change resulting from the initial QA session.

## 4. Requirements traceability matrix

| Requirement area | Result | Evidence and notes |
|---|---|---|
| Seven frozen Phase 1 catalogs | PASS | All seven data files are byte-for-byte unchanged from `c7751b0`; engineering validator passed. |
| Project schema `2.0.0` | PASS | Pydantic model and checked-in generated schema agree. |
| Phase 1 migration | PASS | All 74 pole IDs, folders, names, raw coordinates, and numeric coordinates remained identical; legacy classifications were retained; no family was inferred; repeated migration was idempotent. |
| Invalid migration versions | PASS | Unsupported `0.9.0`, `1.5.0`, and `3.0.0` payloads were rejected with useful diagnostics. |
| Phase 2 contract provenance | FAIL | Operational contracts and their approval wording first appear in implementation commit `39495cf`; no independent pre-implementation proposal is present in Git. |
| Declared JSON Schema draft | FAIL | The three generated Phase 2 schemas validate under an explicitly selected Draft 2020-12 validator but omit the `$schema` declaration claimed by documentation. |
| Generated schema/OpenAPI freshness | PASS | Project schema, OpenAPI, and three operational catalog schemas exactly match current models. |
| Six fixture models | PASS | Phoenix 1 and Solitaire LITE, WIFI, and SMART records exist with stable unique IDs and structured family/variant fields. |
| Fixture capability matrix | PASS | LITE is lighting only; WIFI adds Wi-Fi; SMART adds Wi-Fi and two cameras; all six provide lighting. |
| Family/variant uniqueness | PASS | Enforced by the fixture catalog model. |
| Family-specific electrical/photometric fields | PASS WITH LIMITATION | Separate structured fields exist per model, but authoritative BOM/photometric mappings are not supplied. |
| Phoenix SMART template | PASS | Two active slots at `-70/+70` degrees and 35 degrees down. |
| Solitaire SMART template | PASS | Two active slots at `-60/+60` degrees and 35 degrees down. |
| Absolute azimuth normalization | PASS | Phoenix: `290/70`, `20/160`, `280/60`; Solitaire: `300/60`, `30/150`, `290/50`. |
| Positive downward-tilt convention | PASS | Consistent in contracts, backend, frontend, persistence, documentation, and tests. |
| Template immutability and pinning | PASS | New template revisions append; existing poles remain pinned until explicit adoption. |
| Fixture/camera/lens revision history | FAIL | General catalog edits overwrite the only record; historical versions are not retained. |
| Per-pole override separation | PASS WITH LIMITATION | Overrides do not mutate templates and remain pole-local, but individual override removal is absent. |
| Disabled SMART slots | PASS | Enabled state is keyed by stable slot ID and persists. |
| IES valid upload | PASS | Supported files upload, parse, hash, and retain immutable Base64 bytes and sanitized original basename. |
| IES duplicate handling | PASS | Same SHA-256 deterministically returns the existing record. |
| IES malformed/truncated/unsupported/TILT errors | PASS WITH LIMITATION | Basic negative cases are rejected clearly, but semantic photometric validation is incomplete. |
| IES warning/error representation | FAIL | Operational record has errors but no warning field; invalid/unsupported uploads are not represented as records. |
| IES semantic validation | FAIL | A negative candela value was accepted with `validation_status=valid`. |
| IES many-to-many association/default replacement | PASS WITH LIMITATION | Normal lifecycle works, but inactive files can be re-associated and set as defaults. |
| IES file security | PASS | 20 MB limit, filename basename handling, no filesystem path use from filename, text decoding, and no content execution. |
| Camera/lens separate management | PASS WITH LIMITATION | Separate records and endpoints exist, but revision history is overwritten. |
| Camera/lens compatibility | FAIL | Both reference directions are not required to agree; UI and backend consult different directions. |
| Inactive referenced equipment | FAIL | Deactivating a referenced camera can cause a later project save to return HTTP 500. |
| Missing default lenses | PASS WITH LIMITATION | Clearly shown as unassigned; explicit selection is required before FOV work. |
| Per-pole six-model assignment | PASS | Automated assignment covered all six; rendered controls confirmed capability-driven sections. |
| Model transitions | PASS WITH LIMITATION | Changing model ID resets incompatible hidden configuration, including Phoenix/Smart family changes; detailed transition behavior is not fully documented. |
| Fixture-type/config consistency | FAIL | API accepts a legacy LITE classification combined with a Phoenix SMART configuration. |
| Per-pole save/reopen | PASS | Portable project reopen preserved model, override, source identity, and coordinates. |
| Individual override removal | FAIL | UI shows `Pole override` but exposes no per-slot action to restore inherited behavior. |
| Bulk all/folder | PASS | Folder and all-pole targeting operate deterministically and preserve coordinates. |
| Bulk manual multi-selection | FAIL | Required workflow is absent from the rendered frontend. |
| Bulk explicit-field behavior | FAIL | Explicit `null` for `pole_height_m` erased an existing height. |
| Bulk invalid capability/IES rejection | PASS | Backend validation rejects incompatible camera, Wi-Fi, and IES fields atomically. |
| API status/error behavior | FAIL | Most invalid inputs return useful 4xx responses, but referenced camera deactivation can lead to HTTP 500. |
| Real frontend workflow | PASS WITH LIMITATION | Catalog, IES upload, KML import, legacy selection warning, SMART angles, override, folder bulk, save, and reopen were exercised; required controls are missing as noted. |
| Coordinate preservation | PASS | Embedded, declared, archived, and input hashes match; all source pole coordinate records remained unchanged. |
| Automated regression/build | PASS WITH COVERAGE GAPS | All checked-in tests and build gates pass, but several acceptance requirements have no automated coverage. |

## 5. Contract and migration findings

### Preserved Phase 1 contracts

The following seven data catalogs are byte-for-byte unchanged from the parent contract commit and continue to report schema version `1.0.0`:

- Fixture types.
- Camera catalog.
- Luminaire catalog.
- IES inventory.
- CAP constraints.
- Wi-Fi defaults.
- Calculation-area types.

The engineering-data validator passed all seven schema/data pairs, identifiers, traceability, units, camera bounds, IES hashes/reparsing, source references, CAP unknown-state rules, calculation-area invariants, and supplied-source hashes.

### Phase 2 schemas

The fixture-model, IES-library, and camera-equipment seeds validate under `Draft202012Validator`, and the checked-in schema JSON is current relative to Pydantic. However, unlike the frozen Phase 1 schemas, the three generated Phase 2 schemas omit:

```json
"$schema": "https://json-schema.org/draft/2020-12/schema"
```

This is a deviation from the documented statement that they are declared Draft 2020-12 contracts.

### Approval provenance

At parent commit `c7751b0`, `docs/schema-contracts.md` contains only the seven Phase 1 engineering contracts. The three operational Phase 2 contracts, migration statement, and “Approved by the user on 2026-08-14” language first appear in implementation commit `39495cf`. No separate approved contract/migration-proposal artifact is available for independent comparison. The current operational contracts therefore require explicit retrospective ratification.

### Migration behavior

Migration from Phase 1 `1.0.0` to project schema `2.0.0`:

- Preserves all 74 pole IDs, folders, names, source records, raw coordinate strings, and numeric coordinates.
- Preserves legacy LITE/WIFI/SMART classification edits.
- Does not infer Phoenix 1 or Solitaire.
- Leaves `fixture_configuration` unset.
- Sets `legacy_fixture_assignments_require_model_selection=true`.
- Adds one explicit migration assumption.
- Is deterministic and idempotent for the tested payload.
- Rejects unsupported source versions safely.

## 6. Backend and API findings

The catalog and project endpoints are represented in the generated OpenAPI document, and the document exactly matches the current FastAPI application.

Normal catalog reads, IES uploads and associations, default replacement, project import, bulk patching, project save/open, and export return appropriate successful response codes. Invalid project IDs, path/body ID mismatches, missing catalog records, invalid IES associations, and incompatible non-SMART camera operations normally produce useful 4xx responses.

The following material deviations remain:

- Catalog updates mutate the only camera/lens/fixture record and increment an integer revision without retaining historical content.
- Pole configurations pin a fixture/template revision but camera and lens selections pin only stable IDs.
- Deactivation operations do not evaluate stored project references.
- Project validation can crash when an inactive camera and a lens are both present.
- Compatibility lists can be asymmetric.
- Fixture classification is not checked against selected fixture-model variant.
- Explicit `null` bulk height clears data despite the required empty-field semantics.
- An inactive IES file can be re-associated and promoted to default because default selection checks association activity but not file activity/validation state.

## 7. Frontend and manual workflow findings

The current rendered frontend was run against isolated temporary catalog and project storage. The following workflow was completed:

1. Opened the application and Phase 2 catalog dialog.
2. Confirmed all six fixture models and separate camera/lens records.
3. Uploaded a valid supported IES file through the rendered upload workflow.
4. Imported `Miracle_Mile_Lighting_Poles.kml` and rendered 74 poles.
5. Confirmed the selected legacy pole displayed **Explicit selection required**.
6. Assigned Phoenix 1 SMART and confirmed `-70/+70`, 35-degree-down defaults.
7. Switched to Solitaire SMART and confirmed `-60/+60` defaults.
8. Confirmed LITE/WIFI/SMART controls are derived from structured capabilities.
9. Applied a `-65` degree camera-1 pole override and confirmed it was labeled `Pole override`.
10. Saved and reopened the portable project JSON; the override persisted.
11. Bulk-assigned the ten-pole Decorative folder to Solitaire WIFI at 9.2 m.
12. Confirmed counts changed to LITE 63, WIFI 10, SMART 1.
13. Saved the result and verified source coordinates and embedded source bytes remained unchanged.
14. Confirmed later-phase controls remained disabled.
15. Confirmed no browser console error or warning occurred during the completed workflow.

Manual UI failures/gaps:

- There is no multiple-manually-selected-pole bulk workflow.
- There is no per-slot action to remove an override and restore inheritance.
- Catalog editing is exposed through raw JSON prompt dialogs, which is functional but fragile and not a strong engineering-data management UX.
- Camera/lens historical versions are not viewable because they do not exist in persistence.

Evidence:

![Phase 2 catalog manager](C:/Users/Nadav/.codex/visualizations/2026/08/14/019fff1c-6961-7713-88a7-6f08588d0cc4/phase2-catalogs.png)

![Folder bulk assignment](C:/Users/Nadav/.codex/visualizations/2026/08/14/019fff1c-6961-7713-88a7-6f08588d0cc4/phase2-bulk-folder.png)

## 8. Automated test and build results

### Backend suite

Command:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest -ra
```

Result:

- 37 passed.
- 0 failed.
- 0 skipped.
- One non-failing Starlette/httpx2 deprecation warning.

### Engineering validator

Command:

```powershell
.\.venv\Scripts\python.exe .\scripts\validate_engineering_data.py
```

Result: PASS for seven catalogs, schemas, domain checks, and source hashes.

### Frontend rendered-output tests

The ordinary `pnpm run test` wrapper first attempted an interactive dependency refresh and aborted because the environment had no TTY. To preserve the read-only audit, the already-installed test runner was invoked directly:

```powershell
& 'C:\Users\Nadav\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' --test '.\tests\rendered-html.test.mjs'
```

Result:

- 2 passed.
- 0 failed.
- 0 skipped.

### Strict TypeScript

```powershell
& 'C:\Users\Nadav\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' '.\node_modules\typescript\bin\tsc' --noEmit
```

Result: PASS, zero errors.

### ESLint

```powershell
& 'C:\Users\Nadav\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' '.\node_modules\eslint\bin\eslint.js' . --ignore-pattern dist --ignore-pattern .next
```

Result: PASS, zero errors or warnings.

### Production build

```powershell
$env:Path = 'C:\Users\Nadav\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;' + $env:Path
& 'C:\Users\Nadav\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' run build
```

Result: PASS across client references, server references, RSC, client, and SSR environments.

Warnings/advisories:

- Known non-failing MapLibre-related chunk larger than 500 kB.
- Non-failing Vinext advisory that some routes could not yet be statically classified.

### Generated-contract freshness

In-memory regeneration was compared with checked-in JSON without writing files. Results:

- `project.schema.json`: MATCH.
- `openapi.json`: MATCH.
- `fixture-model-catalog.schema.json`: MATCH.
- `ies-library.schema.json`: MATCH.
- `camera-equipment-catalog.schema.json`: MATCH.

### Meaningful automated-coverage gaps

The checked-in suite does not cover:

- Real frontend interactions.
- The 350-degree SMART azimuth cases.
- Negative or otherwise semantically invalid candela data.
- Inactive referenced camera/lens lifecycle behavior.
- Historical camera/lens/fixture revision retention.
- Per-slot override removal.
- Manual multi-pole selection.
- Explicit-null bulk semantics.
- Fixture classification versus selected-model consistency.
- Reciprocal camera/lens compatibility.
- Inactive IES reassociation/default selection.

## 9. Fixture capability verification

| Model | Lighting | Wi-Fi | Cameras | Result |
|---|---:|---:|---:|---|
| Phoenix 1 LITE | Yes | No | No | PASS |
| Phoenix 1 WIFI | Yes | Yes | No | PASS |
| Phoenix 1 SMART | Yes | Yes | Two | PASS |
| Solitaire LITE | Yes | No | No | PASS |
| Solitaire WIFI | Yes | Yes | No | PASS |
| Solitaire SMART | Yes | Yes | Two | PASS |

IDs are stable and unique; family-plus-variant combinations are unique; behavior is driven from structured capability fields. Phoenix and Solitaire models have separate electrical, photometric, IES, and mounting-template structures, although authoritative values/mappings remain incomplete.

## 10. SMART mounting-geometry verification

### Phoenix 1 SMART

| Fixture azimuth | Camera 1 | Camera 2 | Result |
|---:|---:|---:|---|
| 0° | 290° | 70° | PASS |
| 90° | 20° | 160° | PASS |
| 350° | 280° | 60° | PASS |

Relative offsets are `-70/+70`, separation is 140 degrees, and both slots use positive 35-degree downward tilt.

### Solitaire SMART

| Fixture azimuth | Camera 1 | Camera 2 | Result |
|---:|---:|---:|---|
| 0° | 300° | 60° | PASS |
| 90° | 30° | 150° | PASS |
| 350° | 290° | 50° | PASS |

Relative offsets are `-60/+60`, separation is 120 degrees, and both slots use positive 35-degree downward tilt.

No LITE or WIFI fixture receives a camera mounting template. The slot list is structurally extensible for future counts.

## 11. IES-management verification

Tested results:

| Case | Result |
|---|---|
| Valid LM-63-2002 Type C, `TILT=NONE` upload | PASS |
| Deterministic duplicate handling | PASS |
| Malformed text renamed `.ies` | PASS — rejected clearly |
| Truncated IES | PASS — rejected clearly |
| Unsupported LM-63 version | PASS — rejected clearly |
| Unsupported TILT data | PASS — rejected clearly |
| One IES associated to multiple fixture models | PASS |
| Default association replacement | PASS |
| Incompatible/unassociated pole IES | PASS — rejected |
| Referenced IES deactivation | PASS WITH LIMITATION — references become invalid and associations/defaults are disabled, but catalog lifecycle is not project-aware |
| Original uploaded bytes | PASS — hash/bytes unchanged |
| Failed upload errors | PASS WITH LIMITATION — understandable response, but no invalid/unsupported record or warning collection |
| Negative candela content | FAIL — accepted as valid |
| Inactive IES reassociation/default | FAIL — accepted through inconsistent lifecycle sequence |

## 12. Per-pole and bulk-configuration verification

Per-pole configuration correctly shows model-dependent lighting, Wi-Fi, and SMART controls. Pole height is in metres, fixture azimuth is bounded to `[0, 360)`, camera/lens assignments are slot-keyed, disabled state persists, incompatible active combinations are normally rejected, and portable project reopen retains configuration.

Model changes through the frontend construct a new configuration when the model ID changes, preventing hidden SMART configuration from remaining under a LITE or WIFI model. Phoenix SMART to Solitaire SMART and the reverse reset family-specific camera overrides and adopt the newly selected template.

Failures:

- No individual override removal action.
- Backend accepts inconsistent legacy fixture type and structured model variant.
- Detailed transition retention/clearing policy is insufficiently documented.

Bulk behavior correctly preserves unrelated properties for ordinary non-empty fields and validates the complete copied project before saving, preventing backend partial mutation. Folder/all-pole changes are deterministic, preserve coordinates, and survive save/reopen.

Failures:

- No manually selected multi-pole frontend workflow.
- Explicit `null` height clears an existing value.

## 13. Coordinate-preservation evidence

Representative source: `Input/Miracle_Mile_Lighting_Poles.kml`

- Source poles: 74 before and after configuration.
- First raw coordinate: `-80.26234411,25.74920999,0` before and after.
- First numeric longitude: `-80.26234411` before and after.
- First numeric latitude: `25.74920999` before and after.
- Embedded source size: 34,385 bytes.
- Declared source size: 34,385 bytes.
- Input SHA-256: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
- Embedded SHA-256: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
- Declared SHA-256: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.

No pole source ID, folder, source name, raw coordinate, or numeric source coordinate changed during per-pole or folder-bulk configuration. Customer source data remained separate from edit overlays.

## 14. Defect list

### IR-01 — Major — Catalog revisions overwrite history

Reproduction:

1. Read `camera-imx477` revision 1.
2. Change its display name and PUT the same stable ID.
3. Read the catalog again.

Expected: revision 1 remains available and existing configurations continue referencing its exact content.

Actual: only one record remains, now revision 2; revision 1 is gone. Camera/lens selections are stored only by ID, without a pinned equipment revision. Fixture records have the same issue outside mounting-template history.

Affected components: `backend/app/services/catalogs.py`, `backend/app/catalog_models.py`, `backend/app/models.py`, catalog UI, and pole configuration.

Phase 3 impact: Blocks reproducible FOV and pixel-density calculations.

### IR-02 — Major — Referenced camera deactivation can cause HTTP 500

Reproduction:

1. Configure a SMART pole with `camera-imx477` and `lens-jl-ln039`.
2. Save successfully.
3. Deactivate `camera-imx477`.
4. Save the project again.

Expected: safe conflict/validation response, with the existing project remaining readable and recoverable.

Actual: `500 Internal Server Error` because validation indexes an inactive/missing camera after reporting it unavailable.

Affected component: `backend/app/services/configuration.py`.

Phase 3 impact: Blocks safe catalog/project integration.

### IR-03 — Major — IES validation accepts invalid candela content

Reproduction: upload a complete LM-63-2002 Type C, `TILT=NONE` payload containing one negative candela value.

Expected: rejected as invalid photometric content.

Actual: accepted with `validation_status=valid` and the expected candela count.

Affected component: `backend/app/services/ies.py`.

Phase 3 impact: Blocks the Phase 2 gate and must be fixed before any Phase 5 photometric calculation.

### IR-04 — Major — IES warning/error contract is incomplete

Expected: parsed operational record can represent warnings and errors; declared schema draft is explicit.

Actual: the record has errors but no warnings; failed uploads are not represented as invalid/unsupported records; Phase 2 schemas omit `$schema`.

Affected components: `backend/app/catalog_models.py`, generated Phase 2 schemas, frontend types/UI.

Phase 3 impact: Blocks Phase 2 acceptance; warning fidelity is also required before lighting calculations.

### IR-05 — Major — Inactive IES records can become defaults

Reproduction:

1. Upload and associate an IES.
2. Deactivate it.
3. Reactivate only the association through the association API.
4. Set it as fixture default.

Expected: inactive file cannot have an active association or become a default.

Actual: inactive file becomes the fixture default.

Affected component: `backend/app/services/catalogs.py`.

Phase 3 impact: Blocks Phase 2 acceptance.

### IR-06 — Major — Camera/lens compatibility can become asymmetric

Expected: explicit compatibility has one authoritative interpretation and is enforced consistently.

Actual: camera and lens lists may disagree; the UI consults the lens side while backend project validation consults the camera side.

Affected components: `backend/app/catalog_models.py`, `backend/app/services/configuration.py`, `frontend/app/components/PoleInspector.tsx`.

Phase 3 impact: Blocks reliable camera/lens selection for FOV work.

### IR-07 — Major — Domain-inconsistent project payloads are accepted

Reproduction:

1. Configure a pole as Phoenix 1 SMART.
2. Change only legacy `fixture_type` to `LITE`.
3. PUT the complete project.

Expected: rejected because classification and structured configuration disagree.

Actual: HTTP 200.

Affected component: `backend/app/services/configuration.py`.

Phase 3 impact: Blocks reliable capability decisions.

### IR-08 — Major — Manual multi-pole bulk selection is absent

Expected: manually selected poles, folder, and all-poles targeting.

Actual: rendered UI provides only folder and all-pole targeting.

Affected component: `frontend/app/components/EngineeringWorkspace.tsx`.

Phase 3 impact: Blocks the Phase 2 acceptance gate.

### IR-09 — Major — Empty bulk height erases data

Reproduction:

1. Set a pole height to 9 m.
2. Bulk patch the same pole with `{"pole_height_m": null}`.

Expected: empty field leaves the existing value unchanged.

Actual: HTTP 200 and height becomes null.

Affected component: `backend/app/services/configuration.py`.

Phase 3 impact: Blocks the Phase 2 acceptance gate.

### IR-10 — Major — Individual overrides cannot be removed

Reproduction:

1. Assign Phoenix 1 SMART.
2. Change camera-1 relative azimuth.
3. Observe `Pole override` label.
4. Search the rendered controls for a remove/reset override action.

Expected: remove that override and restore inherited template behavior without resetting the whole pole.

Actual: no per-slot removal action exists; only whole-pole restore is available.

Affected component: `frontend/app/components/PoleInspector.tsx`.

Phase 3 impact: Blocks correct inheritance and revision-adoption workflows.

### IR-11 — Major — Missing approval provenance

Expected: independently reviewable approved Phase 2 contract/migration proposal predates implementation.

Actual: contracts, migration assertion, and approval language first appear with implementation.

Affected component: documentation and review governance.

Phase 3 impact: Requires explicit contract ratification before Phase 2 can close.

## 15. Known limitations and Phase 3 impact

| Known limitation | Impact | Required owner/input |
|---|---|---|
| No authoritative fixture-to-IES/electrical BOM mapping | Catalog framework can operate, but authoritative product/IES assignment and lighting calculations must remain blocked. | Juganu product engineering/BOM and photometric reports. |
| Solitaire 50 W versus 60 W conflict | Inventory can remain, but Solitaire lighting assignment/calculation is unsafe until resolved. | Manufacturer datasheet and photometric lab report. |
| Missing physical camera XYZ offsets | Directly blocks Phase 3 ground-FOV geometry. | Mechanical drawing/installation guide. |
| Missing default SMART lens assignments | Explicit selection is correctly required; FOV/pixel-density calculations must block unassigned slots. | Approved fixture/camera BOM or project-specific engineering selection. |
| IES limited to LM-63-1995/2002 Type C, `TILT=NONE` | Transparent declared limitation; does not itself block camera Phase 3 but constrains later photometric inputs. | Future contract expansion only if additional formats are required. |
| Missing terrain assumption | Independently blocks Phase 3 ground intersection. | Project engineering decision/site data. |

No missing engineering value should be invented.

## 16. Required fixes before Phase 3

1. Implement immutable historical revisions for fixture, camera, and lens records.
2. Pin pole camera and lens assignments to exact catalog revisions or preserve equivalent immutable snapshots.
3. Define safe behavior for deactivated records already referenced by projects and eliminate the validation crash.
4. Harden IES semantic validation, including candela validity, angle arrays/ranges/order, numeric finiteness, and relevant header constraints.
5. Add operational IES warnings and consistent invalid/unsupported error representation.
6. Prevent inactive or invalid IES records from acquiring active associations or defaults.
7. Establish one authoritative camera/lens compatibility relation or enforce strict reciprocity.
8. Validate legacy fixture classification against the selected structured fixture model.
9. Add individual per-slot override removal/restoration.
10. Add manually selected multi-pole bulk targeting.
11. Define and enforce explicit null/empty bulk-patch semantics.
12. Add Draft 2020-12 `$schema` declarations to the Phase 2 operational schemas.
13. Add regression tests for every defect above and meaningful frontend interaction coverage.
14. Explicitly ratify the Phase 2 operational contracts and migration behavior.
15. Obtain camera XYZ offsets, terrain assumptions, and required lens assignments before authorizing Phase 3 geometry.

## 17. Non-blocking recommendations

- Replace raw JSON prompt-based catalog editing with structured forms and field-level validation messages.
- Add an endpoint or UI view that explains why a record cannot be deactivated and lists affected projects/poles.
- Display IES SHA-256, parsed dimensions, angle ranges, warnings, and associations in a dedicated detail view.
- Add transition confirmation when switching fixture models will clear camera overrides.
- Add a visible “inherited from template revision N” provenance indicator per effective camera field.
- Add production UI end-to-end tests for import, catalog upload, six-model assignment, transitions, override/reset, bulk selection, save, and reopen.
- Track the Vinext static-route-classification advisory separately from the accepted MapLibre chunk advisory.

## 18. Final recommendation

Phase 2 remains **FAIL** and Phase 3 must not begin.

The implementation has a strong Phase 1-preservation foundation and correct fixture capability and SMART geometry data, but the Major catalog-lifecycle, IES-validation, compatibility, override, bulk, API-consistency, and approval-provenance defects must be resolved and independently retested. Phase 3 also remains blocked by missing physical camera offsets, lens decisions, and terrain assumptions even after the software defects are fixed.
