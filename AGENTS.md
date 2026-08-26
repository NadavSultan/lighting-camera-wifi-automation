# Repository working agreement

This repository is the independent source of truth for Lighting Camera WiFi Automation. Do not depend on an external Codex skill at runtime.

## Required session startup

Before planning or changing code, every future session must read these files in order:

1. `AGENTS.md`
2. `PROJECT_CONTEXT.md`
3. `docs/current-status.md`
4. `docs/implementation-plan.md`
5. `docs/architecture.md`
6. `docs/data-model.md`
7. `docs/phase-1-completion-report.md`

Then inspect `git status` and preserve unrelated or user-owned changes. Phases 1-4 are accepted and formally closed. Phase 5 planning decisions were approved on 2026-08-26; Phase 5 implementation and later phases remain gated and unauthorized.

## Safety and engineering rules

- Existing-pole mode is the default. Never generate, redistribute, optimize, move, or delete customer poles without explicit user authorization.
- Keep every uploaded source file byte-for-byte unchanged. Store source data, user edits, calculated data, and recommendations separately.
- Treat WGS84 coordinates as interchange/display data only. Select a local projected CRS in metres for distance, area, coverage, or later photometric calculations.
- Do not infer CAP limits, fixture applicability, photometric conventions, or analytics performance. Record an assumption or block the feature.
- Camera downward angle is measured below horizontal: 0 degrees is horizontal and 90 degrees is vertically down.
- Phase work must remain gated. Phases 1-4 are closed. Phase 5 planning and all section-15 decisions were approved on 2026-08-26, but Phase 5 implementation still requires separate explicit authorization.

## Development

- Backend: Python 3.12, FastAPI, Pydantic, PyProj, and defusedxml.
- Frontend: React/TypeScript with MapLibre.
- Add automated tests for every parsing, geometry, calculation, or recommendation engine.
- Preserve fixture colours: LITE red, WIFI yellow, SMART blue; CAP and priority-area colours must remain distinct.
- Never commit runtime projects, ad-hoc uploads, generated exports, caches, virtual environments, or `node_modules`.
- `Input/` contains the supplied, read-only engineering references and is intentionally versioned. Never modify these files in place.

## Phase 1 acceptance

Phase 1 includes project creation, KML/KMZ import, validation, map display, per-pole fixture type/height/status/notes edits, separate edit tracking, JSON save/reopen, updated KML export, and tests. It explicitly excludes proposed pole generation, camera geometry, Wi-Fi coverage analysis, IES calculations, and CAP recommendations.

## Phase boundary

Phase 2 adds operational fixture-model, IES, and camera/lens catalogs; Phase 3 adds fixed-mount camera geometry; Phase 4 adds the explicitly authorized simplified direct-lighting engine. The seven approved Phase 1 engineering catalogs remain frozen at `1.0.0`. Phase 5 planning decisions are locked by its planning contract; do not add Phase 5 Wi-Fi or later calculation/recommendation engines without separate explicit implementation authorization.
