# BL-001 provider authorization — 2026-09-07

Status: **authorized for implementation** (product work not started by this record)

This is an item authorization, not a Phase 8, not a harness seal, and not merge authority.

## User decision

On 2026-09-07 the user authorized BL-001 using the **total free option**:

- **Standard:** keep the current OpenStreetMap raster.
- **Satellite:** EOX Sentinel-2 cloudless via EOX’s **free public WMTS/WMS**, with required attribution. No purchase, no commercial EOX license, no bundled or offline mosaic.
- **Session-only** Standard/Satellite choice.
- **Provider config in environment**, not project JSON.
- **The satellite provider may be replaced later.** Do not bake EOX (or any other provider) into saved projects, source data, edits, calculations, or reports.

## Binding replaceability rule

The product must expose **Standard vs Satellite**, not a hard-wired “EOX” engineering identity.

- Environment/deployment config supplies the satellite tile template, tile size, zoom range, and attribution.
- `.env.example` documents generic names and may show the current authorized EOX free-WMTS example values. Live secrets are forbidden.
- Saved `project.json` and exports must remain provider-agnostic. Changing the satellite source later is a config/authorization change, not a project-schema migration.
- If satellite config is missing or tiles fail, keep OSM and offer return to Standard. Do not drop engineering overlays to recover.

## Current authorized source (first satellite backend)

- **Service:** EOX::Maps public tiles (`https://maps.eox.at/`), Sentinel-2 cloudless.
- **Terms recorded at authorization:** free public WMTS/WMS for non-commercial applications with attribution; demo/service as-is, may change, may rate-limit; no SLA purchased.
- **Credentials:** none. Public client tile URLs only. Do not embed a private server credential in `NEXT_PUBLIC_*`.
- **Exact URL, year mosaic, tile size, zoom, and attribution text:** verify against current official EOX Maps / s2maps documentation **at implementation time**. This record authorizes that class of free public EOX tiles; it does not freeze an unverified XYZ string.

## Still unauthorized

- Commercial EOX license / paid mosaic / offline bundle
- Persisting the background choice or provider identity in project JSON
- OBS-01
- Phase 8 / any new phase seal
- Merge to `main`

## Implementation start identity

Start from Stages 1–7 implementation commit `02c027ef29439aaeef3ca15562be7df0490205d5` on `codex/bl-006-ies-associations` unless a later authorized commit supersedes it. Controlling design: plan Task 8 in `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md`. Stage record: `harness/phases/2026-09-07-stage-8-bl-001-gated.md`.
