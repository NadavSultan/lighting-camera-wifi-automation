# Project context

## Product

Lighting Camera WiFi Automation is a local, map-centred engineering application for customer-supplied lighting pole layouts. The primary workflow preserves customer coordinates while engineers classify poles as LITE, WIFI, or SMART and progressively add lighting, camera, Wi-Fi, and CAP engineering data.

## Current repository state

Phases 1 through 7 are accepted and formally closed after independent QA and their master gate decisions. The FastAPI and React/TypeScript MapLibre application includes operational catalogs, fixed SMART mounting templates, camera geometry, separate lighting calculation areas, deterministic Type C direct-light calculations, conceptual Wi-Fi circles/overlap/area statistics, CAP / JNET1 distance-graph and constraint planning with persisted provenance, and Phase 7 deterministic multi-format report packages. Phase 4 remains explicitly simplified and is not professionally validated against AGi32 or another reference tool; Phase 5 remains conceptual geometry and is not verified RF design; Phase 6 remains conceptual graph planning and is not RF, performance, compliance, or installation validation; Phase 7 reports are engineering-review artifacts only. Existing-pole mode is mandatory and proposed-layout mode is unavailable. Actual Miracle Mile CAP operational values remain unknown unless separately approved.

Phase 7 closed on 2026-09-05: accepted implementation `e24b6a1`, Independent QA PASS, master gate PASS, and valid seal `harness/seals/phase-07.md`. Post-roadmap work remains unauthorized.

New sessions must start with `AGENTS.md` and `docs/current-status.md`, then follow the remaining reading order recorded in `AGENTS.md`.

## Supplied references

- `Input/Miracle_Mile_Lighting_Poles.kml`: 74 valid WGS84 point placemarks in five folders; no exact coordinate or name duplicates found during initial inventory.
- `Input/Lighting/`: four LM-63-2002 IES files. Photometric implementation is the gated Phase 4 scope.
- `Input/Camera/VideoCAD Camera Models - Juganu.Xlsx`: three pinned IMX477-compatible camera/lens records used by the operational catalog and Phase 3 geometry.
- `Input/CAP/CAP datasheet.pdf`: Juganu JNET1 Gateway data sheet Rev 1.2, retained as source evidence for the accepted Phase 6 planning model.

The requested `$lighting-kml-planner` skill was not installed or discoverable during Phase 1. No application code depends on it.

## Known input gaps

- Pole mounting heights and per-pole fixture assignments.
- Professional-reference validation and manufacturer confirmation of the approved MVP photometric orientation assumption.
- Final per-pole lens assignments remain explicit. The Phase 3 MVP approves zero XYZ camera-origin offsets and fixed two-slot template orientation.
- Project boundary and classified calculation polygons.
- CAP applicability by fixture type, recommended operating distance, siting/backhaul/electrical constraints, required redundancy, and installation-specific band selection.

See `docs/reference-input-inventory.md` for the auditable inventory.

## Phase 1 handoff summary

- The supplied KML imports as 74 preserved point placemarks in five folders and selects `EPSG:32617` for projected checks.
- Source uploads are archived unchanged; user edits are separate, reversible overlays.
- JSON Schema and OpenAPI contracts are generated into `schemas/`.
- Backend tests, frontend rendered-output tests, strict TypeScript checking, lint, production build, and local startup are the handoff acceptance commands.
- Runtime data under `backend/data/projects/`, build output, caches, and dependencies are ignored by Git.

See `docs/phase-1-completion-report.md` for the completion evidence and `docs/current-status.md` for the exact next task.
