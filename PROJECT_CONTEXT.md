# Project context

## Product

Lighting Camera WiFi Automation is a local, map-centred engineering application for customer-supplied lighting pole layouts. The primary workflow preserves customer coordinates while engineers classify poles as LITE, WIFI, or SMART and progressively add lighting, camera, Wi-Fi, and CAP engineering data.

## Current repository state

Phases 1 and 2 are implemented, tested, and accepted. The repository contains a FastAPI backend and React/TypeScript MapLibre frontend with operational fixture-model, IES, camera/lens, per-pole, and bulk-configuration workflows. Existing-pole mode is mandatory and proposed-layout mode is unavailable.

New sessions must start with `AGENTS.md` and `docs/current-status.md`, then follow the remaining reading order recorded in `AGENTS.md`.

## Supplied references

- `Input/Miracle_Mile_Lighting_Poles.kml`: 74 valid WGS84 point placemarks in five folders; no exact coordinate or name duplicates found during initial inventory.
- `Input/Lighting/`: four LM-63-2002 IES files. Photometric implementation is deferred to Phase 5.
- `Input/Camera/VideoCAD Camera Models - Juganu.Xlsx`: three IMX477 camera/lens records. Catalog implementation is deferred to Phase 2.
- `Input/CAP/CAP datasheet.pdf`: Juganu JNET1 Gateway data sheet Rev 1.2. CAP implementation is deferred to Phase 6.

The requested `$lighting-kml-planner` skill was not installed or discoverable during Phase 1. No application code depends on it.

## Known input gaps

- Pole mounting heights and per-pole fixture assignments.
- Authoritative luminaire-to-IES mapping, verified wattage/flux values, and photometric orientation conventions.
- Camera XYZ offsets and final per-pole lens assignments. The two-slot relative-azimuth templates are approved in Phase 2.
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
