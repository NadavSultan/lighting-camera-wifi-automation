# BL-016 QA-03 scoped implementation verification — 2026-09-29

Implementation identity: `ca7f46c57a28028bd96b8e40926f50e3e4932edc` (detached worktree). Starting identity: `b384bda5ad5c6e4c7175772284d0473ebe10339a`. This verifies only the Satellite public build-time configuration correction from the independent QA finding; BL-016 is not accepted.

## Root cause and correction

The original configured production build embedded the local API URL but emitted `readSatelliteConfigFromEnv({})` in the browser chunk, so Satellite was reported unconfigured. The whole `process.env` object did not preserve the `NEXT_PUBLIC_SATELLITE_*` values through Vinext's browser compilation. The correction passes five direct public `process.env.KEY` references to the existing provider-neutral reader. The production build now fails if a configured value is missing from the client chunks. The failing-first integration test rejected the old configured bundle, then passed after the correction. The unconfigured build intentionally skips the bundle assertion, and existing helper tests still cover Standard fallback.

## Current deterministic checks on implementation commit

| Check | Result | Warning or limit |
|---|---|---|
| Backend `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` from `backend/` | PASS, 364 tests | Starlette/httpx and AnyIO deprecations |
| Engineering data validator | PASS, eight catalogs/source hashes | none |
| Frozen frontend dependency installation | PASS, lockfile unchanged | supply-chain policy metadata 22 days old |
| Frontend test/typecheck/lint | PASS, 107 tests; no type/lint errors | none |
| Production build with API `:8070` and all five approved EOX public variables set **before** build | PASS; integrated configured client-bundle test 1/1 | plugin timing, >500 KB chunk, dynamic-route classification advisories |
| Schema exporter and `git diff --exit-code -- schemas` from repository root | PASS, byte-fresh | first hash command from backend used wrong relative path; corrected root check passed |
| `git diff --exit-code -- Input frontend/pnpm-lock.yaml`, KML SHA-256, `git diff --check` | PASS; KML `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328` | no source/lockfile edits |
| Existing isolated BL-016 live harness retry01 | PASS, 12/12 API and production-shell assertions | first attempt failed transient `3070` bind before server start; both outputs preserved |

## Rendered seam

`harness/verify/2026-09-29-bl-016-qa03-browser.json` records the actual production browser import of 74 customer poles, Satellite selection, approved EOX attribution, 16 observed EOX tile-fetch image resources, one successfully retrieved JPEG from that inventory, and no browser console warnings/errors. The approved EOX tile probe returned HTTP 200 with JPEG content. The first sandboxed direct probe was denied by local socket policy; an authorized read-only retry succeeded. Standard attribution returned after switching back.

The browser also configured one Phoenix 1 SMART pole (10 m, both cameras pinned to JL-LN037), calculated a current camera-density result, and retained that result across Standard/Satellite switches. All ten visible legend swatches matched exactly. The shared MapLibre density layers still define 0.58 fill opacity, and the 107-test frontend run includes the canonical colour/opacity check. The in-app screenshot interface returned unavailable, and browser scope did not expose the MapLibre paint property directly; this is a scoped implementation smoke, not a claim of visual-pixel or full interactive acceptance.

## Boundary and gate

Only four frontend implementation files changed in `ca7f46c5`: `EngineeringWorkspace.tsx`, `satellite-production-bundle.integration.mjs`, `package.json`, and `README.md`. All later changes are harness evidence. `Input/`, catalogs, geometry, backend, generated schemas, lockfile, and the separate independent-QA worktree were unchanged. Independent QA remains FAIL on its last recorded report until it re-reviews this correction. No master PASS, seal, merge, or push is claimed.
