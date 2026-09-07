# Independent QA review — 2026-09-07 — BL-001

Verdict: **PASS**

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: **dirty worktree** on branch `codex/bl-006-ies-associations` at HEAD `1febc8768ffac3ef38b212028867dab34790bff9`. Product and harness changes are **uncommitted**. There is **no** sealed implementation commit. Identity is this live dirty tree, not a clean commit. The worktree was preserved (no reset/clean/stash/revert/merge).
- Controlling contract, phase record, and acceptance IDs: `docs/post-roadmap-backlog.md` BL-001; plan Task 8 in `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md`; provider authorization `docs/post-roadmap-bl-001-provider-authorization-2026-09-07.md`; stage record `harness/phases/2026-09-07-stage-8-bl-001-gated.md`; handoff `harness/verify/2026-09-07-bl-001-independent-qa-handoff.md`. Acceptance IDs `BL001-01`–`BL001-04`. Item process (no Phase 8; `verify_phase_readiness.py` not used as a gate).
- Reviewer/session independence: fresh Independent QA session. Implementer work record, execution log, and `harness/verify/2026-09-07-bl-001-verification.md` treated as **claims only**. Git identity, live diff, source, helper, frontend commands, engineering validator, and EOX WMTS/tile checks were re-run or re-inspected on this tree.
- Review scope: BL-001 only — session-only Standard/Satellite map background; first authorized satellite backend = free non-commercial EOX public WMTS with required attribution; environment/`.env.example` config names; no project-JSON provider identity.
- Non-goals and excluded phases: **no** OBS-01 correction; **no** project-schema change; **no** baking a provider into saved projects; **no** commercial/paid mosaic; **no** Phase 8 / harness seal; **no** merge; **no** BL-001 acceptance (requires this QA PASS **and** a later scoped master decision). No product implementation or defect repair was performed.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Branch/HEAD `1febc876`; dirty BL-001 tree preserved; authorized file boundary; no Phase 8 seal; OBS-01 still present; schema hash unchanged | PASS |
| Deterministic verification | Frontend typecheck/lint/test/build; focused `map-background.test.mjs`; engineering/source validator; `Input/` clean; no backend/schema/OpenAPI mutation so backend pytest not required | PASS |
| Acceptance-matrix review | `BL001-01`–`BL001-04` inspected against helper, wiring, env example, live WMTS/tile fetch, and current commands | PASS |
| Rendered/manual workflow | Live MapLibre Standard/Satellite matrix (active polygon draft, Wi-Fi/CAP, lighting labels/card, direction arrows, failed config, attribution, min/max zoom, resize, overlay survival) **not independently executed** | deferred (labeled residual risk) |
| Source/prior-phase regression review | `Input/` diff empty; `project.schema.json` hash `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e`; `SOFTWARE_VERSION` `0.7.0`; no backend engine/schema/OpenAPI edits; OBS-01 still `key={warning}` | PASS |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| BL001-01 Standard/Satellite choice works with approved provider | Code + helper + independent EOX WMTS/tile fetch | Workspace overlay buttons labeled **Standard** / **Satellite** (`aria-pressed` session state). `BASE_STYLE` remains OSM raster. Satellite is environment-configured via `readSatelliteConfigFromEnv` / `NEXT_PUBLIC_SATELLITE_*`. Independent GET `https://tiles.maps.eox.at/wmts/1.0.0/WMTSCapabilities.xml` HTTP 200: layer `s2cloudless-2025_3857`, TileMatrixSet `g` / `GoogleMapsCompatible`, JPEG ResourceURL `{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}`, 256 px tiles. HTTPS tile `.../g/0/0/0.jpg` HTTP 200 `image/jpeg` (JPEG magic `ff d8 ff`). z19 HTTP 404 matches example `MAX_ZOOM=18`. `.env.example` XYZ is `g/{z}/{y}/{x}.jpg` over **HTTPS** (WMTS ResourceURL host is `http://`; HTTPS tiles were verified). Helper `backgroundAvailability` matches the plan fixture. **Live MapLibre with this env was not run.** | PASS |
| BL001-02 viewport, draft and all overlays survive switching | Static/code inspection of map init and update path. **Not** helper tests as live overlay proof | `EngineeringMap.tsx` has **no** `.setStyle(` after init. Satellite `addSource`/`addLayer` runs on `load` **before** poles/FOV/Wi-Fi/CAP/draft layers, so the raster sits under engineering layers. Switching uses `setLayoutProperty` visibility only (`backgroundLayerVisibility`). `fitBounds` still keyed to `project.id`, not background. Draft GeoJSON, layer visibility, lighting canvas labels, direction canvas, and React lighting card/background overlays are not torn down by a style replace. Helper tests assert `addSource("satellite")` and no `setStyle`; they **do not** prove live overlay survival. **Live repeated switching with an active polygon draft, Wi-Fi/CAP layers, lighting labels/card, and direction arrows was not independently executed.** | PASS (static mechanism only; live overlay survival is residual risk, not a helper-test PASS) |
| BL001-03 attribution/error/fallback are correct | Helper + workspace wiring + WMTS abstract | Missing config → `Satellite imagery is not configured`, choice resets to standard, OSM stays, **Use standard map** offered. Tile failure → OSM visible, OSM attribution, `SATELLITE_LOAD_FAILED`, **Use standard map**. Successful satellite session uses config attribution and hides OSM. Compact `AttributionControl` remains; satellite source spec carries env attribution. WMTS 2025 abstract: EOxCloudless / Copernicus Sentinel data 2025 / CC BY-NC-SA 4.0; `https://maps.eox.at/` asks for a link back. Env attribution includes EOxCloudless, Copernicus 2025, and `https://maps.eox.at`. **Live failed-tile and on-map attribution chrome were not independently executed.** | PASS |
| BL001-04 no credential leakage, unapproved service use, project migration or source mutation | Diff + grep + hashes + env file + helper | No backend/schema/OpenAPI/lockfile edits vs `1febc876`. `project.schema.json` git hash still `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e`. `SOFTWARE_VERSION` / API `0.7.0`. `Input/` diff empty. `types.ts` / schemas / reports have no satellite/EOX/provider fields. `downloadProjectJson` stringifies the `Project` object unchanged. Workspace `backgroundChoice` is React `useState` only; no `setProject`/`mutateProject` of a background/provider. Helper has no `eox` / `s2cloudless`. `.env.example` has public tile URL + names, no secrets (`git check-ignore` via existing `frontend/.gitignore` `.env*`). HTTPS-only helper rejects `http://` and userinfo credentials. First backend is the authorized free public EOX WMTS, not a purchased mosaic. OBS-01 untouched. | PASS |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git status --short --branch`; `git rev-parse HEAD`; `git branch --show-current` | dirty @ `1febc876` | branch `codex/bl-006-ies-associations`; HEAD match; dirty product + harness | Uncommitted; preserved |
| `git diff --name-status` / `--stat` vs `1febc876` | dirty @ `1febc876` | product: `EngineeringMap.tsx`, `EngineeringWorkspace.tsx`, `globals.css`, `frontend/README.md`; created `map-background.mjs` / `.d.mts` / `map-background.test.mjs`; gitignored `frontend/.env.example` present on disk; execution-index/harness updates | No extra unauthorized product paths. No backend/schema/OpenAPI/lockfile/`Input/` |
| `git hash-object schemas/project.schema.json` | dirty @ `1febc876` | `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e` | Unchanged vs required hash |
| `git diff --exit-code -- Input` | dirty @ `1febc876` | exit 0 | Protected sources unchanged |
| `SOFTWARE_VERSION` / OpenAPI version inspection | dirty @ `1febc876` | `0.7.0` in `backend/app/models.py` and `backend/app/main.py` | No version bump |
| OBS-01 still present | dirty @ `1febc876` | `key={warning}` in `CapPlanningPanel.tsx` (109, 297), `ReportPanel.tsx` (232), `PoleInspector.tsx` (91) | Not corrected, as authorized |
| `harness/seals/` | dirty @ `1febc876` | `phase-06.md`, `phase-07.md`, `README.md` only | No Phase 8 seal created |
| Independent EOX WMTS GET + HTTPS tile GET | dirty @ `1febc876` | capabilities HTTP 200 (67911 bytes); layer `s2cloudless-2025_3857`; z0 JPEG 200; z19 404 | Confirms example config class; not a MapLibre walkthrough |
| `node --test tests/map-background.test.mjs` (from `frontend/`) | dirty @ `1febc876` | exit 0; **9 passed**, 0 failed | Plan helper fixtures + source-string guards |
| Frontend `corepack pnpm run typecheck` | dirty @ `1febc876` | exit 0 | `tsc --noEmit` |
| Frontend `corepack pnpm run lint` | dirty @ `1febc876` | exit 0 | ESLint; no errors/warnings printed |
| Frontend `corepack pnpm run build` | dirty @ `1febc876` | exit 0 | Vinext production build. Non-failing advisory: client chunk > 500 kB; some routes unclassified |
| Frontend `corepack pnpm run test` (after build) | dirty @ `1febc876` | exit 0; **58 passed**, 0 failed | Includes new map-background tests + existing rendered-html suite |
| `scripts/validate_engineering_data.py` | dirty @ `1febc876` | PASS | 7 catalogs; supplied-source hashes valid |
| Backend pytest | — | **not run** | Live diff does not touch backend/schema/OpenAPI; skip matches the required rule |
| Live MapLibre browser matrix (plan Task 8 / BL-001 verification) | — | **not run** | No browser MCP; no Playwright in `.venv` or `frontend/node_modules`. Residual risk. **Not** treated as a helper-test PASS for BL001-02 overlay survival |

Historical implementer logs/verify files guided selection only and were not substituted for the commands above.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| QA-BL001-LIVE | Info | BL001-02 live overlay survival; Task 8 browser matrix | Live MapLibre walkthrough (Standard/Satellite with approved EOX env; repeated switching with an active polygon draft, Wi-Fi/CAP layers, lighting labels/card, direction arrows; failed/missing config; attribution chrome; min/max zoom; viewport resize; overlays survive) was **not independently executed**. Helper tests and static `setStyle` absence cannot prove runtime overlay survival. | Scoped master may require a live pass before merge, or formally accept this residual risk. Do not treat this row as a product defect. |
| QA-BL001-ATTR | Minor | BL001-03 / WMTS Abstract | Env attribution credits EOxCloudless, Copernicus Sentinel data 2025, and `https://maps.eox.at`, but omits the WMTS Abstract license sentence (CC BY-NC-SA 4.0) and commercial-usage pointer. maps.eox.at link-back is present. | Optional: include the license sentence in `NEXT_PUBLIC_SATELLITE_ATTRIBUTION` if master wants the full Abstract. Not required to PASS BL001-03. |
| QA-BL001-ENV | Info | File boundary / `.env*` gitignore | `frontend/.env.example` exists on disk (1453 bytes) and is ignored by existing `frontend/.gitignore` `.env*`, as the handoff required to confirm. Exact EOX XYZ is therefore **not git-tracked**. README documents generic `NEXT_PUBLIC_SATELLITE_*` names and the replaceable first backend class. | Master/commit planning may need a gitignore exception or a tracked example if the XYZ must survive clone. Not a dirty-tree product defect. |
| OBS-01 | Info (out of scope) | Duplicate React keys | Warning lists still key by warning text (`key={warning}`). Not corrected, as authorized. | Separate authorization only. |

No Critical or Major product defects confirmed. Requirements were not weakened. No extra provider-specific product paths were found outside the authorized Task 8 boundary plus expected harness/execution-index updates.

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [x] Every mandatory acceptance item independently disposed as PASS or recorded as a blocking finding.
- [x] Required deterministic checks completed on the exact reviewed dirty worktree; live MapLibre matrix labeled residual risk and **not** used as a helper-test PASS for BL001-02 overlay survival.
- [x] Source preservation, no project-schema/provider persistence, prior-phase exclusion, OBS-01/Phase 8 exclusion verified.
- [x] Verdict is supported without relying on unverified implementer claims.

## Recovery protocol

1. Preserve this QA file and dirty-tree identity `1febc876` plus the uncommitted BL-001 product/harness files.
2. Record that live MapLibre was not available in this session.
3. If implementation changes, invalidate affected QA rows and retest the new exact tree.
4. Do not reset/clean/stash to “make” a clean commit without separate authorization.

## Allowed stopping conditions

- QA is complete and the supported PASS verdict is recorded. QA never authorizes a scoped master PASS, merge, or a seal.

## Verdict and next gate

- Verdict: **PASS** (item-based Independent QA for BL-001 only).
- Open findings: Info `QA-BL001-LIVE` (deferred live MapLibre matrix / residual overlay-survival risk); Minor `QA-BL001-ATTR`; Info `QA-BL001-ENV`; OBS-01 unchanged/excluded.
- Master gate eligibility: **not eligible from this review alone**. Worktree is uncommitted; live MapLibre matrix is deferred; this review is **not** BL-001 acceptance, **not** a scoped master PASS, **not** merge authorization, and **not** a harness seal.
- Exact next action: a later **scoped master decision** for BL-001 (and any required live browser pass or commit authorization). Do **not** merge. Do **not** create Phase 8 or any harness seal from this review. Do **not** fix OBS-01.

## File-boundary notes (non-blocking)

Authorized Task 8 product paths observed:

- Modified: `frontend/app/components/EngineeringMap.tsx`, `frontend/app/components/EngineeringWorkspace.tsx`, `frontend/app/globals.css`, `frontend/README.md`
- Created: `frontend/app/lib/map-background.mjs`, `frontend/app/lib/map-background.d.mts`, `frontend/tests/map-background.test.mjs`, `frontend/.env.example` (gitignored; present on disk)

Expected harness/execution-index updates: `GOALS.md`, `PLANS.md`, `docs/post-roadmap-backlog.md`, `harness/phases/2026-09-07-stage-8-bl-001-gated.md`, plus untracked work record / execution log / implementer verification / QA handoff.

No provider-specific extra product paths requiring a boundary finding were observed. Backend, `schemas/`, OpenAPI, lockfiles, and `Input/` were not mutated.
