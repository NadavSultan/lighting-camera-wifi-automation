# Verification — 2026-09-07 — BL-001

Item: BL-001 Standard/Satellite session-only background. Not a phase seal. Not merge. Not BL-001 acceptance.

| Field | Value |
|---|---|
| Branch | `codex/bl-006-ies-associations` |
| Base / HEAD | `1febc8768ffac3ef38b212028867dab34790bff9` |
| Implementation identity | dirty worktree on that HEAD (product + harness; `frontend/.env.example` present but ignored by existing `frontend/.gitignore` `.env*`) |
| Independent QA | pending |
| Master / seal | not requested; `harness/seals/phase-08.md` absent |

## Provider facts verified at execution time (2026-09-07)

Official public EOX::Maps WMTS (`https://tiles.maps.eox.at/wmts/1.0.0/WMTSCapabilities.xml`, HTTP 200):

- Layer: `s2cloudless-2025_3857`
- TileMatrixSet: `g` / `GoogleMapsCompatible`
- Tile size: 256×256 JPEG (SOF and live tiles)
- XYZ for MapLibre: `https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2025_3857/default/g/{z}/{y}/{x}.jpg`
- Native zoom: 0–18 confirmed live; z19 and z21 returned 404
- Attribution (WMTS Abstract): EOxCloudless https://cloudless.eox.at by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2025), CC BY-NC-SA 4.0; `https://maps.eox.at/` also requests a link back to EOX::Maps
- HTTPS tiles work; capabilities ResourceURL lists `http://` (not used in the example)

These values are documented only in `frontend/.env.example` and `frontend/README.md`. Product UI is Standard vs Satellite.

## Acceptance

| ID | Result | Evidence |
|---|---|---|
| BL001-01 | PASS (deterministic / source / SSR) | Helper availability + raster spec; workspace Standard/Satellite selector; `EngineeringMap` adds `satellite` source/layer under engineering layers without `setStyle`; production SSR HTML contains Standard and Satellite (`status 200`) |
| BL001-02 | PASS with residual live MapLibre | Session state is React-only; visibility toggles `osm`/`satellite` layout; no style replace; overlays/drafts are unchanged map sources. Live click/switch with an active draft was **not** run (no browser MCP / Playwright) |
| BL001-03 | PASS (helper + wiring) | Missing config → OSM + `Satellite imagery is not configured`; tile failure → OSM + `SATELLITE_LOAD_FAILED` + `Use standard map`; OSM attribution unchanged; satellite attribution from config |
| BL001-04 | PASS | HTTPS-only tiles; credentials in URL rejected; no `NEXT_PUBLIC` secrets in repo; `Input/` diff empty; project schema hash `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e` unchanged; no backend/schema/OpenAPI edits; helper has no EOX identity; OBS-01 untouched |

## Commands (this worktree, 2026-09-07)

| Check | Result |
|---|---|
| `corepack pnpm run typecheck` (frontend) | exit 0 |
| `corepack pnpm run lint` | exit 0 |
| `corepack pnpm run test` | exit 0; **58 passed**, 0 failed |
| `corepack pnpm run build` | exit 0; chunk-size advisory and unclassified-route note only |
| `git diff --exit-code -- Input` | exit 0 |
| `git hash-object schemas/project.schema.json` | `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e` |
| Live MapLibre browser matrix (plan §13/§14) | **not run** |

## File boundary

In-boundary: `EngineeringMap.tsx`, `EngineeringWorkspace.tsx`, `globals.css`, `frontend/README.md`, `map-background.mjs` / `.d.mts`, `map-background.test.mjs`, `frontend/.env.example`, this item’s harness records.

Out of boundary and unchanged: backend engines, `models.py`, `schemas/`, `Input/`, OBS-01, Phase 8 seal.

## Handoff

Implementation is ready for **independent QA**. Do not treat this record as BL-001 acceptance. Do not merge. Do not create a harness seal. A later scoped master decision is required. A later commit, if authorized, must `git add -f frontend/.env.example` because `.env*` ignores it; do not amend `.gitignore` without a boundary change.
