# Engineering Data & Specifications completion report

Completion date: 2026-08-13

Scope: technical-source inventory, traceable catalogs, schemas, conventions, assumptions/open questions, and validation only. No Phase 2 application behavior, geometry, calculation, coverage, recommendation, or pole-generation feature was implemented.

## Handoff result

**PASS.** Seven structured catalogs validate against seven Draft 2020-12 schemas. All four IES files reparse with the recorded headers and complete candela counts. All catalog source references exist, and SHA-256 checks confirm the original KML, PDF, XLSX, and four IES files remain byte-for-byte unchanged.

The repository is ready for an Engineering Data Acceptance Review and, after explicit approval, Phase 2 catalog integration. It is not ready for final camera geometry, RF prediction, photometric calculation, or CAP recommendation because the open engineering inputs below remain unresolved.

## Files inspected

### Required repository handoff

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `README.md`
- `docs/architecture.md`
- `docs/data-model.md`
- `docs/implementation-plan.md`
- `docs/current-status.md`
- `docs/phase-1-completion-report.md`
- `docs/phase-1-validation-report.md`
- `docs/reference-input-inventory.md`
- Existing backend/frontend models, tests, schemas, package configuration, and project structure
- Git status and latest commit `51273af62cc745ba34f6efb6089607a312a9b05c`

### Technical sources

| Source | SHA-256 | Inspection result |
|---|---|---|
| `Input/Miracle_Mile_Lighting_Poles.kml` | `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` | Existing 74-pole/five-folder inventory retained; no calculation polygons present. |
| `Input/Camera/VideoCAD Camera Models - Juganu.Xlsx` | `7f5e3858b237c353a184edd3324fffa9a1571adb0b94174d48f28a1868b5dd72` | One sheet, three IMX477 lens rows; cells and workbook metadata inspected. |
| `Input/CAP/CAP datasheet.pdf` | `2a1692daef1f3e0537c9c84b144a5063e2041add1e970bbf27a25dad1bb52bce` | All five pages text-extracted, rendered, and visually reviewed. |
| `Input/Lighting/JLED-SL-100W-PHOENIX1-40-D01.ies` | `4a897fb04b6d8f6c75c94a3ceba473391021aee6d506f05357f48bc01d26d363` | Complete LM-63-2002 Type C dataset. |
| `Input/Lighting/JLED-SL-120W-PHOENIX1-40-D01.IES` | `eb05f9cc5064ab6a0fa19e2886ff0af9cecfa06a7f2ef0bc2e269e57929173c1` | Complete LM-63-2002 Type C dataset. |
| `Input/Lighting/JLED-GL-050W-SOLITAIRE 3B-D01.IES` | `fda02adb7ca11c6ca5af8e930bdc5e1b8ffb5f558eb8a432a7d4fae87e18db38` | Complete dataset; 50 W/header versus 60W/internal-model conflict. |
| `Input/Lighting/JLED-GL-050W-SOLITAIRE 3B-D02.ies` | `4efa14cfe43e2214080bcd09d6424b353322010c07717106bc3218297839c86a` | Complete dataset; wattage conflict and negative width/length warning. |

No standalone luminaire datasheets, separate lens datasheets, network design guide, or additional customer KML/KMZ examples were available.

## Values and records created

- Fixture types: LITE, WIFI, and SMART with internally checked lighting/Wi-Fi/camera capabilities and unresolved CAP participation.
- Cameras: one shared IMX477 camera/sensor record and three lens records (JL-LN039, JL-LN042, JL-LN037). Exact 4056 x 3040 dimensions are included because the workbook confirms them. The 12 MP value is retained as the company-provided nominal class.
- Luminaires: four provisional catalog records linked one-to-one with their IES files.
- IES: four inventories with hashes, keywords, LM-63 header fields, dimensions, angle counts/ranges, Type C/metre interpretation, warnings/errors, and luminaire associations. Every file has 73 vertical angles, 145 horizontal angles, and 10,585 candela values.
- CAP/JNET1: base product, four ordering variants, 29 manufacturer constraints/capabilities, one derived terminology mapping, and 11 explicit missing recommendation inputs. No CAP engineering assumption was introduced.
- Wi-Fi: 30 m conceptual radius for WIFI/SMART only, with 13 excluded RF factors and an explicit non-prediction disclaimer.
- Calculation areas: Road, Sidewalk, Parking, and Other; 0.00 m plane; 2.00 m X/Y grid; polygon clipping; separate polygon statistics; and five required statistics. Lighting targets remain null.

## Assumptions introduced

- The 30 m Wi-Fi circle is a temporary conceptual engineering assumption.
- A photometric rotation order is proposed for later AGi32 validation but is not implemented or treated as approved.
- Project term CAP is provisionally mapped to the supplied JNET1 Gateway/Group Controller document as a derived terminology mapping, not a product requirement.

No camera FOV conflict, luminaire wattage conflict, CAP range/load/hop target, redundancy rule, or RF-performance value was resolved by assumption.

## Missing information and blocking dependencies

- Camera: JL-LN037 87/90 degree FOV decision; manufacturer/enclosure model; quantity; lens assignment rules; mounting axes/offsets; azimuth; analytics criteria.
- Luminaire/IES: product datasheets; Solitaire orderable model/wattage mapping; flux; CCT; mounting heights; fixture compatibility; optic definitions; C0-plane/housing mapping; D02 negative-dimension interpretation; test report IDs; AGi32 validation method/tolerances.
- Wi-Fi: actual RF bands, antennas/heights, EIRP, propagation inputs, interference/channel/client/throughput requirements, and backhaul limits.
- CAP: node-type applicability; recommended design distance/load/hops; antenna/LOS; site band; redundancy; power/backhaul availability; siting constraints.
- KML/KMZ/calculation: project boundary and classified polygons, folder-assignment authority, grid origin/boundary rules, maintenance factor, and approved illuminance/uniformity targets.
- Reporting: required deliverables, units/precision, disclaimers, signatures, and citation granularity.

The full risk and ownership register is `docs/engineering-open-questions.md`.

## Created files

- Seven JSON catalogs under `data/`
- Seven JSON Schemas under `schemas/`
- `scripts/validate_engineering_data.py`
- `backend/tests/test_engineering_data.py`
- Seven engineering convention/assumption/open-question documents under `docs/`
- This completion report

Updated files are `backend/pyproject.toml`, `docs/current-status.md`, and `docs/reference-input-inventory.md`.

## Validation evidence

- Engineering data validator: **PASS** - seven catalogs/schemas; unique identifiers; traceability; approved units/statuses; source existence; camera bounds; fixture consistency; Wi-Fi applicability; IES reparsing/counts/associations/hashes; CAP missing-value policy; calculation-area invariants; all source hashes.
- Backend: **23 passed**, one existing non-failing Starlette/httpx deprecation warning.
- Frontend rendered-output tests: **2 passed, 0 failed**.
- TypeScript: **passed**, zero errors.
- ESLint: **passed**, zero errors or warnings.
- Production build: **passed** across client, server, RSC, and SSR; existing non-failing MapLibre chunk-size advisory remains.

The frontend package wrapper initially requested non-interactive permission to reconcile `node_modules`; the exact underlying locked test, TypeScript, ESLint, and Vinext build commands were run against the existing installation and passed.

## Phase 2 readiness and next session

The schema/catalog foundation is ready for review and application integration after explicit authorization. Source conflicts are safely represented and will not masquerade as verified values. Phase 2 should begin only with an **Engineering Data Acceptance Review and Phase 2 Catalog Integration Planning** session that approves the contracts and resolves or explicitly carries the JL-LN037 and Solitaire discrepancies. Phase 3-6 engines remain gated.
