# Scoped master decision — post-roadmap BL Stages 1–7

Date: 2026-09-07

Decision: **CONDITIONAL PASS** (accept-with-conditions)

This is an **item-based scoped master decision**. It is **not** a phase seal, **not** Phase 8, and **not** authorization of BL-001 or OBS-01.

## Identity reviewed

| Field | Value |
|---|---|
| Repository | lighting-camera-wifi-automation (workspace root with `AGENTS.md`) |
| Branch | `codex/bl-006-ies-associations` |
| HEAD (docs tip, not rolled back) | `71d4d5248f5460268b9993e9f405693b8aa2434e` |
| Reviewed application ancestor | `8751714003bf09f39c217a5f26b9fd6056d2927b` (`merge-base --is-ancestor` exit 0) |
| Implementation identity | **dirty worktree** on that HEAD (tracked modifications + untracked product/harness files) |
| Sealed implementation commit | **none** — the dirty tree is not an accepted commit identity |

Independent QA PASS: `harness/verify/2026-09-07-post-roadmap-bl-1-7-independent-qa-review.md` (claim set; not treated as proof).

## Item set

Authorized and decided here: **BL-003, BL-006, BL-002, BL-008, BL-007, BL-004, BL-005**.

Explicitly excluded / gated:

- **BL-001** remains gated until a separate imagery-provider authorization. No satellite selector, no `map-background` helper, Stage 8 record remains `harness/phases/2026-09-07-stage-8-bl-001-gated.md`.
- **OBS-01** remains uncorrected by authorized exclusion (`key={warning}` still present, including in new CAP panel copy of the existing pattern).
- **Phase 8** was not invented. `harness/seals/phase-08.md` is absent. Readiness verifier was not used as the item gate.
- Phases 1–7 remain formally closed. This decision does not reopen or amend those contracts.

## Verdict

Accept the Stages 1–7 item set **with conditions**.

All mandatory acceptance IDs `BL003-01`–`BL003-04`, `BL006-01`–`BL006-04`, `BL002-01`–`BL002-04`, `BL008-01`–`BL008-05`, `BL007-01`–`BL007-04`, `BL004-01`–`BL004-04`, and `BL005-01`–`BL005-05` are **PASS** on the reviewed dirty tree, with Independent QA PASS corroborated by master identity/boundary inspection and master re-runs listed below. No Critical or Major product defect was confirmed. Requirements were not weakened.

**Conditions (all binding):**

1. The dirty tree is **not** a sealed implementation commit. Acceptance of product quality on this worktree does not mint a commit SHA.
2. **Commit is authorized** (one bounded implementation commit of the reviewed tree plus this decision file). See file list below.
3. **Merge is not authorized** by this decision. Do not merge to `main` until a later explicit authorization binds a real commit SHA.
4. Residual findings `QA-PR-01` and `QA-PR-02` are accepted without remediation. `QA-PR-03` deferral is accepted (see dispositions). Live MapLibre remains an unverified residual risk, not a FAIL of this CONDITIONAL record.
5. BL-001, OBS-01, Phase 8, and any harness seal remain unauthorized.

## What master re-ran vs accepted from QA

### Independently re-run by master (2026-09-07, this dirty tree @ HEAD `71d4d52`)

| Check | Result |
|---|---|
| `git status --short --branch`; `git rev-parse HEAD` | branch `codex/bl-006-ies-associations`; HEAD match; implementation uncommitted; preserved |
| `git merge-base --is-ancestor 8751714 HEAD` | exit 0; docs tip `71d4d52` not rolled back |
| File-boundary / name-only vs plan Tasks 1–7 + recorded collateral | product paths match authorized items; no engine files (`lighting_calculation.py`, `wifi_coverage.py`, `cap_planning.py`, `catalogs.py`, `models.py`) in the diff |
| `git diff --exit-code -- Input` | exit 0 |
| `git hash-object schemas/project.schema.json` vs `HEAD:` | identical `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e` |
| Live OpenAPI vs `schemas/openapi.json` (Python compare, **no file write**) | `openapi_equal True`; version `0.7.0`; preview path present; **only added path vs HEAD** is `/api/fixture-directions/preview` |
| Lockfiles | no diff (`backend/requirements.lock`, `frontend/pnpm-lock.yaml`) |
| `SOFTWARE_VERSION` / OpenAPI info version | remain `0.7.0` |
| `scripts/validate_engineering_data.py` | PASS (7 catalogs; supplied-source hashes valid) |
| Backend pytest `-q -p no:cacheprovider --basetemp %TEMP%\lcwa-m-fd33f8ed` | exit 0; **297 passed**; Starlette/httpx deprecation warnings only |
| Frontend `corepack pnpm run typecheck` / `lint` / `build` / `test` | all exit 0; **49 passed**, 0 failed; build chunk-size advisory and unclassified-route note only |
| `git diff --check HEAD` on product paths | exit 0 |
| No `harness/seals/phase-08.md`; no `frontend/app/lib/map-background.*` | confirmed absent |
| Spot-check of draft layers, IES pending guard, Wi-Fi explicit show action, CAP summary, preview non-mutation tests, OBS-01 still present | corroborated QA’s product claims on those points |

### Accepted from Independent QA without repeating the same command

| Check | Disposition |
|---|---|
| Focused backend slice 16+28+31+15+66 = 156 | Covered by master’s full 297-test run |
| Write-producing `export_schema` | Not re-run (would mutate the dirty tree). Replaced by live OpenAPI equality + project-schema hash |
| Per-ID wiring narrative beyond master’s spot-checks | Accepted after corroborating the controlling helpers, map draft registration, preview route, and UI entry points |
| Implementer per-item logs/verify files | Historical/self-check only; not substituted for master commands |

### Not run by master (same limitation as QA)

| Check | Disposition |
|---|---|
| Live production MapLibre browser matrix (plan §6–12 and combined §14 walkthrough) | **Not run.** No Playwright in `.venv` or `frontend/node_modules`; no browser MCP in this session. Finding `QA-PR-03`. |
| Combined 74-pole production UI walkthrough | **Not run.** Residual risk under `QA-PR-03`. |

## Finding dispositions

| ID | Severity | Master disposition |
|---|---|---|
| QA-PR-01 | Minor | **Accept. No remediation required** before commit. Confirmed: `useEffect` depends on `[fixtureDirectionKey, project]`, so non-orientation project updates also POST preview. Sequence counter + `AbortController` still drop late bodies. BL005-04 remains PASS. Optional later cleanup: depend on `fixtureDirectionKey` only. |
| QA-PR-02 | Minor | **Accept. No remediation required** before commit. QA overstated the request race: `toggle()` already returns if any `pendingId` is set, so overlapping association **requests** cannot start. Only the checkbox `disabled` attribute is per-row (`pendingId === row.id`), so other boxes still look enabled. Residual UX only. Optional later cleanup: disable all association controls for that file while pending. |
| QA-PR-03 | Info | **Accept deferral.** Do **not** fail this CONDITIONAL item-master for lack of a live MapLibre pass. Helper tests, production SSR/`rendered-html` suite, and code review of MapLibre source/layer registration are not a substitute for the plan’s browser matrix, but they are sufficient to avoid rejecting the item set. Live walkthrough remains residual risk and is **recommended** against the future implementation commit; it is **not** a blocker of this CONDITIONAL record and is **not** authorized as new product work. |
| OBS-01 | Info (excluded) | **Unchanged / not authorized.** Do not correct duplicate React keys without separate authorization. |

No bounded remediation file list. Worktree left intact.

## Commit authorization (yes) and required identity

**Commit: authorized.** **Merge: not authorized.** **Push: not authorized by this decision.**

The exact implementation identity required after commit is **the SHA of one new commit** on `codex/bl-006-ies-associations` that contains the reviewed dirty product/harness tree plus this decision file, and does **not** contain caches, `node_modules`, virtualenvs, `frontend/dist` / `.next` runtime output, or `backend/data` runtime projects.

Until that SHA exists, there is **no** accepted implementation commit. After it exists, this CONDITIONAL PASS binds to that SHA only if the committed tree matches the reviewed set (no extra product files, no omitted required files). A follow-up identity confirmation (`git status` clean, `rev-parse HEAD`) is required before any later merge authorization. This decision does **not** itself perform that bind.

### Files authorized in that commit

Tracked modifications:

- `GOALS.md`, `PLANS.md` (execution-index status only; a one-line update citing this CONDITIONAL PASS is permitted in the same commit)
- `backend/app/main.py`
- `frontend/app/components/CatalogManager.tsx`
- `frontend/app/components/EngineeringMap.tsx`
- `frontend/app/components/EngineeringWorkspace.tsx`
- `frontend/app/globals.css`
- `frontend/app/lib/api.ts`
- `frontend/package.json` (test script glob only)
- `frontend/tests/rendered-html.test.mjs`
- `schemas/openapi.json`

Untracked product / tests:

- `backend/app/services/fixture_direction_preview.py`
- `backend/tests/test_fixture_direction_preview.py`
- `frontend/app/components/CapPlanningPanel.tsx`
- `frontend/app/components/IesAssociations.tsx`
- `frontend/app/components/LightingPointLabels.tsx`
- `frontend/app/components/LightingResultCard.tsx`
- `frontend/app/components/WifiMapSummary.tsx`
- `frontend/app/lib/cap-workflow-view.mjs` + `.d.mts`
- `frontend/app/lib/fixture-direction-view.mjs` + `.d.mts`
- `frontend/app/lib/ies-association-view.mjs` + `.d.mts`
- `frontend/app/lib/lighting-card-position.mjs` + `.d.mts`
- `frontend/app/lib/lighting-labels.mjs` + `.d.mts`
- `frontend/app/lib/polygon-draft.mjs` + `.d.mts`
- `frontend/app/lib/wifi-map-state.mjs` + `.d.mts`
- `frontend/tests/cap-workflow-view.test.mjs`
- `frontend/tests/fixture-direction-view.test.mjs`
- `frontend/tests/ies-association-view.test.mjs`
- `frontend/tests/lighting-card-position.test.mjs`
- `frontend/tests/lighting-labels.test.mjs`
- `frontend/tests/polygon-draft.test.mjs`
- `frontend/tests/wifi-map-state.test.mjs`

Harness / decision evidence:

- `harness/phases/2026-09-07-stage-0-prep.md`
- `harness/phases/2026-09-07-stage-8-bl-001-gated.md`
- `harness/phases/2026-09-07-bl-00{2,3,4,5,6,7,8}-work-record.md`
- `harness/logs/2026-09-07-bl-00{2,3,4,5,6,7,8}-execution.md`
- `harness/verify/2026-09-07-bl-00{2,3,4,5,6,7,8}-verification.md`
- `harness/verify/2026-09-07-post-roadmap-bl-1-7-independent-qa-review.md`
- `docs/post-roadmap-bl-1-7-scoped-master-decision-2026-09-07.md` (this file)

Do **not** commit runtime projects, ad-hoc uploads, generated exports, caches, virtual environments, or `node_modules`. Do **not** modify `Input/`.

## Gate decision

| Question | Answer |
|---|---|
| Stages 1–7 item set accepted | YES, with conditions above |
| Unconditional / sealed implementation commit | NO |
| Commit authorized | YES (bounded list; one commit) |
| Merge authorized | NO |
| Push authorized | NO |
| Project-control docs may invent Phase 8 or amend Phase 1–7 seals | NO |
| Dependent BL-001 authorized | NO |
| OBS-01 authorized | NO |
| Harness seal created or authorized | NO |
| `verify_phase_readiness.py` used as item gate | NO |

## Exact next authorized action

**Create the single bounded implementation commit described above** on `codex/bl-006-ies-associations`, preserving the rest of the worktree (do not reset/clean/stash/revert). Record the new SHA. Do **not** merge. Do **not** start BL-001. Do **not** fix OBS-01. Do **not** create `harness/seals/` entries.

After that commit, a separate identity-bind / merge authorization is required. A live MapLibre walkthrough against that SHA is recommended residual verification, not new product scope.

## Residual documentation debt (non-blocking)

Several per-item work records still read as `active` / `in progress` even though verification summaries exist. That is record hygiene, not a product defect. Optional cleanup may ride in the authorized commit; it is not required for this CONDITIONAL PASS.
