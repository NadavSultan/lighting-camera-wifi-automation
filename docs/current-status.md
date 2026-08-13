# Current status

Last updated: 2026-08-13. Independent Phase 1 validation is complete and passed after six confirmed defects were fixed. Scope remains frozen at Phase 1. Phase 2 has not started and is not authorized.

## Completed features

- Local FastAPI and React/TypeScript application with a MapLibre-centred engineering workspace.
- New project, KML/KMZ import, local project save, portable project JSON reopen/export, and updated KML export.
- Safe XML parsing and KMZ checks for traversal, archive count/size, and compression ratio.
- Extraction of valid Point placemarks while retaining the unchanged uploaded source bytes.
- Preservation of folder hierarchy, names, KML IDs, descriptions, ExtendedData, source style URL/colour, exact coordinate text, numeric coordinates, and altitude.
- Warnings for malformed coordinates, unsupported geometries, exact/near duplicates, and geographic outliers without automatic correction.
- Deterministic IDs when source placemarks have no ID.
- Existing-pole mode enforced by schema and UI; no proposed pole API or UI exists.
- Interactive selection and map layers for LITE, WIFI, and SMART using the approved red/yellow/blue colours.
- Per-pole edits for name, engineering ID, fixture type, pole height, active status, and engineering notes.
- Folder/all-poles bulk fixture assignment, undo/redo, layer toggles, and restoration of source/default values.
- Separate source and edit layers; coordinate edits require an explicit backend authorization flag and are not exposed by the Phase 1 UI.
- Atomic filesystem project persistence and immutable archived source copies.
- Embedded-source hash, size, safe-filename, and source-record verification when portable project JSON is opened.
- Unique internal pole IDs, with warnings and preserved source IDs when customer KML repeats a Placemark ID.
- Finite coordinate validation and inline KML IconStyle colour resolution.
- Checked-in Pydantic-derived project JSON Schema and OpenAPI contract.
- Inventory and review notes for the supplied KML, four IES files, camera workbook, and CAP datasheet.

## Incomplete features

These are intentionally outside Phase 1 and must not be treated as defects in this handoff:

- Luminaire and IES catalogs or assignments.
- Camera catalog, multiple-camera configuration, FOV geometry, and analytics-quality modelling.
- Conceptual Wi-Fi circles, gap/overlap analysis, and boundary coverage statistics.
- Calculation-area drawing, grids, IES parsing, photometric calculations, statistics, and heat maps.
- CAP constraint model, recommendations, topology, and revalidation.
- Proposed-layout mode or any automatic pole generation/optimization.
- CSV/XLSX/KMZ/PDF and later-phase engineering report outputs.
- UI actions for manual pole coordinate changes, addition, or deletion. The backend model can represent explicitly authorized coordinate edits, but the Phase 1 UI keeps coordinates locked.

## Independent validation result

- Result: **PASS after fixes**. No confirmed Phase 1 correctness defect remains open.
- Findings fixed: one Critical source-integrity/persistence defect, one High duplicate-ID defect, two Medium defects (non-finite coordinates and a failing frontend lint gate), and two Low defects (structured API error display and inline-style metadata).
- The requested simple, nested-folder, ExtendedData, Style/StyleMap, duplicate, malformed/partial, unsupported-geometry, empty, and resource-bearing KMZ cases are now covered by repeatable backend tests.
- Live production UI validation passed for the supplied 74-pole KML: map workspace load, per-pole SMART/height/notes edits, 10-pole WIFI bulk assignment, undo/redo, save, export, and portable JSON reopen.
- Source input, embedded source, and archived source SHA-256 values matched. Updated-KML reimport retained 74 poles with zero coordinate mismatches and preserved fixture metadata in ExtendedData.

See `docs/phase-1-validation-report.md` for finding evidence and the full validation matrix.

## Known limitations

- The OpenStreetMap background requires internet access; pole/project data remain local.
- The production build reports an advisory client chunk larger than 500 kB because MapLibre is bundled with the workspace. Build output is valid.
- Automated rendered-output tests verify the server-rendered shell and phase gating; they do not click through MapLibre canvas interactions.
- FastAPI's current `TestClient` emits a Starlette deprecation warning about future `httpx2` migration; all tests pass.
- Updated KML is an interchange/export artifact. Reimport preserves coordinates and `lcwa_*` ExtendedData, but does not recreate `pole_edits`; portable project JSON is the supported lossless reopen format.

## Tests and build results

Final independent validation on 2026-08-13:

- Backend: `22 passed`; one non-failing Starlette deprecation warning.
- Frontend rendered-output suite: `2 passed`, `0 failed`.
- TypeScript: zero errors.
- ESLint: zero errors or warnings.
- Production build: successful across client, server, RSC, and SSR; one non-failing MapLibre chunk-size advisory.
- Fresh backend startup on validation port 8010: health returned `{"status":"ok","phase":1,"version":"0.1.0"}`.
- Fresh production frontend startup on the documented port 3000: HTTP 200 and the expected application title.

The repeatable command set is:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest

Set-Location ..\frontend
pnpm run test
pnpm run typecheck
pnpm run lint
pnpm run build
```

## Current run commands

From the repository root, start the backend:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second PowerShell terminal, start the frontend:

```powershell
Set-Location .\frontend
pnpm run dev
```

Open `http://localhost:3000/`. API health is `http://127.0.0.1:8000/api/health`; interactive API documentation is `http://127.0.0.1:8000/docs`.

For a new machine/session without dependencies, follow `README.md` first.

## Important architecture decisions

- Customer source data is authoritative and immutable; changes are overlays.
- WGS84 is used for KML/map interchange, while project-local UTM is selected for metre-based checks.
- Existing-pole mode is the only available Phase 1 mode.
- Backend Pydantic models are the authoritative data contract; JSON Schema and OpenAPI are generated artifacts.
- Project JSON embeds source bytes for portable reopen and reproducibility.
- Filesystem persistence is local runtime state and is intentionally ignored by Git.
- The frontend updates fixture classification immediately but later calculation/recommendation engines remain disabled.
- No runtime dependency on the unavailable `$lighting-kml-planner` skill exists.

## Exact next recommended task

Review `docs/phase-1-validation-report.md` and decide whether to formally accept Phase 1. Do not propose or begin Phase 2 until the user explicitly authorizes it after reviewing this validation result.
