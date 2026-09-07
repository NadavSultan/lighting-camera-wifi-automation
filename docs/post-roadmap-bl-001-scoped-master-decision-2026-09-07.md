# Scoped master decision — post-roadmap BL-001

Date: 2026-09-07

Decision: **CONDITIONAL PASS** (accept-with-conditions)

This is an **item-based scoped master decision for BL-001 only**. It is **not** a phase seal, **not** Phase 8, **not** merge authority, and **not** a reopen of Stages 1–7.

Stages 1–7 CONDITIONAL PASS remains `docs/post-roadmap-bl-1-7-scoped-master-decision-2026-09-07.md` (implementation commit `02c027ef`).

## Identity reviewed

| Field | Value |
|---|---|
| Repository | lighting-camera-wifi-automation (workspace root with `AGENTS.md`) |
| Branch | `codex/bl-006-ies-associations` |
| HEAD | `1febc8768ffac3ef38b212028867dab34790bff9` (`docs: authorize BL-001 free EOX tiles as a replaceable satellite backend`) |
| Implementation identity | **dirty worktree** (uncommitted product + harness + Independent QA review/handoff) |
| Sealed implementation commit | **none** — the dirty tree is not an accepted commit identity |

Independent QA PASS (claim set): `harness/verify/2026-09-07-bl-001-independent-qa-review.md`.

Provider authorization: `docs/post-roadmap-bl-001-provider-authorization-2026-09-07.md`.

## Authorized product (unchanged)

- **Standard:** current OpenStreetMap raster.
- **Satellite:** environment-configured public tiles. First authorized backend = free non-commercial EOX Sentinel-2 cloudless public WMTS with required attribution.
- **UI:** session-only **Standard** vs **Satellite** (not an EOX identity).
- **Config:** environment / `.env.example` names only; no live secrets; not project JSON.
- Provider remains **replaceable**. Do not bake a provider URL, mosaic year, or “EOX” into saved projects, source, edits, calculations, or reports.

## Verdict

Accept BL-001 **with conditions**.

Acceptance IDs `BL001-01` through `BL001-04` are **PASS** on this dirty tree after master identity/boundary inspection and master re-runs listed below. Independent QA PASS is corroborated, not rubber-stamped. No Critical or Major product defect was confirmed. Requirements were not weakened. `verify_phase_readiness.py` was not used as the item gate.

**Conditions (all binding):**

1. The dirty tree is **not** a sealed implementation commit.
2. **Commit is authorized** (one bounded implementation commit of the reviewed tree plus this decision file). `frontend/.env.example` is ignored by existing `frontend/.gitignore` `.env*` and **must be included with `git add -f`**. Do not amend `.gitignore`.
3. **Merge, push, Phase 8, and any harness seal remain unauthorized.**
4. Residual `QA-BL001-LIVE` is accepted as deferral (same pattern as Stages 1–7 `QA-PR-03`). Helper tests are **not** live overlay-survival proof.
5. Residual `QA-BL001-ATTR` is accepted without remediation. OBS-01 remains excluded.

## Acceptance IDs

| ID | Master result | Evidence independently inspected |
|---|---|---|
| BL001-01 | PASS | Workspace buttons **Standard** / **Satellite**; OSM `BASE_STYLE` retained; satellite from `NEXT_PUBLIC_SATELLITE_*` via provider-agnostic `map-background.mjs`. `.env.example` (1453 bytes, gitignored) documents verified 2025 3857 HTTPS XYZ, 256 px, zoom 0–18. Helper tests 9/9. **Live MapLibre with this env was not run by master.** |
| BL001-02 | PASS (static mechanism; live residual) | `EngineeringMap.tsx` has **no** `setStyle(` after init. Satellite `addSource`/`addLayer` on `load` **before** poles/FOV/Wi-Fi/CAP/draft layers. Switching uses `setLayoutProperty` visibility only. Helper tests do **not** prove live overlay survival. |
| BL001-03 | PASS | Missing config → standard + “Satellite imagery is not configured” + **Use standard map**. Tile failure → OSM visible + `SATELLITE_LOAD_FAILED` + **Use standard map**. Success uses env attribution. Live attribution chrome not independently executed. |
| BL001-04 | PASS | No backend/schema/OpenAPI/lockfile/`Input/` mutation vs `1febc876`. `project.schema.json` hash `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e`. `SOFTWARE_VERSION` `0.7.0`. `types.ts` has no satellite/provider fields. `downloadProjectJson` stringifies `Project` unchanged. `backgroundChoice` is React session state only. Helper has no `eox` / `s2cloudless`. HTTPS-only helper rejects `http://` and URL userinfo. |

## Finding dispositions

| ID | Severity | Master disposition |
|---|---|---|
| QA-BL001-LIVE | Info | **Accept deferral.** Do not fail this CONDITIONAL record. Live MapLibre Task 8 walkthrough (repeated Standard/Satellite switching with an active polygon draft, Wi-Fi/CAP, lighting labels/card, direction arrows, failed config, attribution chrome, min/max zoom, resize) was **not** independently executed here (no Playwright / browser MCP). Recommended against the future implementation commit; **not** a merge blocker of this CONDITIONAL record and **not** new product work. |
| QA-BL001-ATTR | Minor | **Accept. No remediation required.** Env attribution credits EOxCloudless, Copernicus Sentinel data 2025, and `https://maps.eox.at`. It omits the WMTS Abstract CC BY-NC-SA 4.0 sentence (present in `.env.example` comments). Optional later: add that license sentence to `NEXT_PUBLIC_SATELLITE_ATTRIBUTION`. |
| QA-BL001-ENV | Info | **Not a product defect.** File exists on disk and is ignored by existing `.env*`. **Commit condition:** `git add -f frontend/.env.example` so the verified example XYZ survives clone. Do not change `.gitignore`. |
| OBS-01 | Info (excluded) | **Unchanged / not authorized.** `key={warning}` remains in `CapPlanningPanel.tsx`, `ReportPanel.tsx`, `PoleInspector.tsx`. |

No bounded remediation file list. Worktree left intact except for this decision file.

## What master re-ran vs accepted from QA

### Independently re-run by master (2026-09-07, this dirty tree @ HEAD `1febc876`)

| Check | Result |
|---|---|
| `git status --short --branch`; `git rev-parse HEAD` | branch `codex/bl-006-ies-associations`; HEAD match; dirty product + harness preserved |
| `git diff --name-status` vs `1febc876` | Task 8 product paths + expected harness/execution-index only. No extra unauthorized product paths. No backend/schema/OpenAPI/lockfile/`Input/` |
| `git diff --exit-code -- Input` | exit 0 |
| `git hash-object schemas/project.schema.json` | `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e` |
| `SOFTWARE_VERSION` | `0.7.0` |
| OBS-01 still present | confirmed |
| `harness/seals/` | `phase-06.md`, `phase-07.md`, `README.md` only; no Phase 8 |
| No `setStyle(` in frontend | confirmed |
| Satellite raster added under engineering layers | confirmed |
| UI labels Standard/Satellite; helper provider-agnostic | confirmed |
| `frontend/.env.example` on disk; `git check-ignore` via `frontend/.gitignore:32:.env*` | 1453 bytes; ignored |
| `node --test tests/map-background.test.mjs` | exit 0; **9 passed** |
| Frontend `corepack pnpm run typecheck` / `lint` / `build` / `test` | all exit 0; **58 passed**, 0 failed; chunk-size advisory and unclassified-route note only |
| `scripts/validate_engineering_data.py` | PASS (7 catalogs; supplied-source hashes valid) |
| `git diff --check` vs `1febc876` | exit 0 |
| Backend pytest | **not run** — live diff does not touch backend/schema/OpenAPI |

### Accepted from Independent QA without repeating the same command

| Check | Disposition |
|---|---|
| Independent GET of EOX WMTS capabilities and z0/z19 HTTPS tiles | Accepted after inspecting `.env.example` against that documented class; not re-fetched by master |
| Per-ID wiring narrative beyond master’s spot-checks | Accepted after corroborating map init order, session state, and helper tests |
| Implementer work record / execution log / verification | Historical/self-check only |

### Not run by master (same limitation as QA)

| Check | Disposition |
|---|---|
| Live production MapLibre Task 8 walkthrough | **Not run.** Finding `QA-BL001-LIVE`. |

## Commit authorization (yes) and required identity

**Commit: authorized.** **Merge: not authorized.** **Push: not authorized.**

The exact implementation identity required after commit is **the SHA of one new commit** on `codex/bl-006-ies-associations` that contains the reviewed dirty product/harness tree plus this decision file, **including** `frontend/.env.example` via `git add -f`. Do **not** commit caches, `node_modules`, virtualenvs, `frontend/dist` / `.next`, or `backend/data` runtime projects.

Until that SHA exists, there is **no** accepted BL-001 implementation commit. After it exists, this CONDITIONAL PASS binds to that SHA only if the committed tree matches the reviewed set. A follow-up identity confirmation (`git status` clean, `rev-parse HEAD`) is required before any later merge authorization.

### Files authorized in that commit

Tracked modifications:

- `GOALS.md`, `PLANS.md` (execution-index; a one-line update citing this CONDITIONAL PASS is permitted)
- `docs/post-roadmap-backlog.md`
- `frontend/README.md`
- `frontend/app/components/EngineeringMap.tsx`
- `frontend/app/components/EngineeringWorkspace.tsx`
- `frontend/app/globals.css`
- `harness/phases/2026-09-07-stage-8-bl-001-gated.md`

Untracked product / tests:

- `frontend/app/lib/map-background.mjs`
- `frontend/app/lib/map-background.d.mts`
- `frontend/tests/map-background.test.mjs`

Gitignored example (force-add):

- `frontend/.env.example`

Harness / decision evidence:

- `harness/phases/2026-09-07-bl-001-work-record.md`
- `harness/logs/2026-09-07-bl-001-execution.md`
- `harness/verify/2026-09-07-bl-001-verification.md`
- `harness/verify/2026-09-07-bl-001-independent-qa-handoff.md`
- `harness/verify/2026-09-07-bl-001-independent-qa-review.md`
- `harness/verify/2026-09-07-bl-001-scoped-master-handoff.md`
- `docs/post-roadmap-bl-001-scoped-master-decision-2026-09-07.md` (this file)

## Gate decision

| Question | Answer |
|---|---|
| BL-001 item set accepted | YES, with conditions above |
| Unconditional / sealed implementation commit | NO |
| Commit authorized | YES (bounded list; `git add -f frontend/.env.example`) |
| Merge authorized | NO |
| Push authorized | NO |
| Phase 8 / harness seal authorized | NO |
| OBS-01 authorized | NO |
| Project-schema / provider-in-JSON authorized | NO |
| `verify_phase_readiness.py` used as item gate | NO |

## Exact next authorized action

**Create the single bounded implementation commit described above** on `codex/bl-006-ies-associations`, using `git add -f frontend/.env.example`. Preserve the rest of the worktree (do not reset/clean/stash/revert). Record the new SHA. Do **not** merge. Do **not** push. Do **not** fix OBS-01. Do **not** create `harness/seals/` entries.

After that commit, a separate identity-bind / merge authorization is required. A live MapLibre walkthrough against that SHA is recommended residual verification, not new product scope.
