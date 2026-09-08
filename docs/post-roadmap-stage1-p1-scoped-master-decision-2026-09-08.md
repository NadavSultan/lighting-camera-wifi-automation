# Scoped master decision — post-roadmap Stage 1 P1 display reliability

Date: 2026-09-08

Decision: **CONDITIONAL PASS** (accept-with-conditions)

This is an **item-based scoped master decision for Stage 1 P1 only** (BL-009, BL-005 follow-up, BL-010, BL-011). It is **not** a phase seal, **not** Phase 8, **not** merge authority, and **not** authorization of Stage 2+ (BL-012 through BL-020).

Prior item masters remain in force:

- Stages 1–7: `docs/post-roadmap-bl-1-7-scoped-master-decision-2026-09-07.md` (implementation commit `02c027ef`)
- BL-001: `docs/post-roadmap-bl-001-scoped-master-decision-2026-09-07.md`

## Identity reviewed

| Field | Value |
|---|---|
| Repository | lighting-camera-wifi-automation (workspace root with `AGENTS.md`) |
| Branch | `codex/bl-006-ies-associations` |
| HEAD | `bc45b63da41092175f7fbda97bc4c24f1f39bfe9` (`fix: keep lighting results interactive and calculate every area grid`) |
| `git merge-base --is-ancestor bc45b63 HEAD` | exit **0** |
| Implementation identity | **dirty worktree** on that HEAD (tracked frontend presentation files + untracked scheduler/tests/harness/QA) |
| Sealed implementation commit | **none** — the dirty tree is not an accepted commit identity |

Independent QA PASS (claim set): `harness/verify/2026-09-08-stage1-p1-independent-qa-review.md`.

Controlling contract: `docs/web-app-review-2026-09-08.md` WA-01..WA-04; `docs/post-roadmap-backlog.md` 2026-09-08 intake; work record `harness/phases/2026-09-08-stage1-p1-display.md`.

## Item set

Authorized and decided here: **BL-009 / WA-01**, **BL-005 follow-up / WA-02**, **BL-010 / WA-03**, **BL-011 / WA-04**.

Explicitly excluded / gated:

- **Stage 2+** (BL-012 through BL-020), including WA-05 card anchoring and later web-audit items
- **Merge to `main`**, push, Phase 8, any harness seal
- Engine, schema, catalog, `Input/`, and lockfile changes
- Invented azimuths or Miracle Mile CAP operational values
- Phase 1–7 reacceptance
- `verify_phase_readiness.py` as an item gate

## Verdict

Accept Stage 1 P1 **with conditions**.

Acceptance IDs WA-01/BL-009, WA-02/BL-005 follow-up, WA-03/BL-010, and WA-04/BL-011 are **PASS** on this dirty tree after master identity/boundary inspection, master re-runs listed below, and corroboration of Independent QA’s live MapLibre JSON and screenshot set. No Critical or Major product defect was confirmed. Requirements were not weakened.

**Conditions (all binding):**

1. The dirty tree is **not** a sealed implementation commit. Acceptance of product quality on this worktree does not mint a commit SHA.
2. **Commit is authorized** (one bounded implementation commit of the reviewed tree plus this decision file). See file list below.
3. **Merge, push, Phase 8, and any harness seal remain unauthorized.** Do **not** start Stage 2.
4. Info findings `QA-S1-01` through `QA-S1-05` are accepted without remediation.
5. Residual coverage listed below (125% zoom/keyboard, azimuths 90/180/270, WIFI-yellow live arrow, CAP “Show selected”) is accepted. It is **not** a FAIL of this CONDITIONAL record and is **not** new product work.

## Acceptance IDs

| ID | Master result | Evidence independently inspected |
|---|---|---|
| WA-01 / BL-009 | PASS | CSS: `.app-shell` / `.workspace` 100% width and `overflow: hidden`; inspector column `minmax(0, 318px)`. Live QA JSON: 1920 / 1440 / 1366 / 1024 `workspaceRight` / `inspectorRight` / `topbarRight` = `innerWidth`; `overflowX` false. Collapse `inspectorLeft` 1878. Screenshots `prod-layout-*.png` and `prod-04-collapsed.png` present. |
| WA-02 / BL-005 follow-up | PASS | Shared scheduler `cancelMapFrame` clears the stored id. `FIXTURE_ARROW_COLORS` remain LITE `#ef4444` / WIFI `#facc15` / SMART `#3b82f6`. Live QA: unconfigured overlay painted; after explicit Phoenix 1 SMART, SMART-blue arrow; `.azimuth-handle` count 1; preview directions used (no invented north default). Prod+dev screenshots present. |
| WA-03 / BL-010 | PASS | Labels use the same scheduler. Live calculate stored 1638 points. Labels remained painted after pan, zoom-in, Control-drag rotate, and 1920→1440 resize (canvas width 1324→844). No lighting-engine or grid-spacing edit. CAP Show-selected skipped (`QA-S1-01`). |
| WA-04 / BL-011 | PASS | Card `max-height: min(420px, calc(100% - 24px))` — not a 220 px clip. Core stats (Eavg/Emin/Emax/Emin/Eavg/Emin/Emax) present; `statsFullyVisible` true; body 113 = 113. Assumptions in `<details>`. Header `preventDefault` / `stopPropagation` on pointer down. |

## Finding dispositions

| ID | Severity | Master disposition |
|---|---|---|
| QA-S1-01 | Info | **Accept. No remediation required.** CAP “Show selected sites on map” was not executed because the test-only feasible action was unavailable. Pan/zoom/rotate/resize evidence is sufficient for BL-010. Optional later live CAP `easeTo` is not required to reverse this PASS and is not Stage 2 authorization. |
| QA-S1-02 | Info | **Accept. Closed for this tree.** Independent copy-canvas sampling returned non-zero painted pixels. Implementer INCONCLUSIVE headless sample is superseded. |
| QA-S1-03 | Info | **Accept. No remediation required.** Zero lux is an eligible-IES gap, not a clip defect and not BL-017. |
| QA-S1-04 | Info | **Accept. No remediation required.** WIFI-yellow live arrow not configured this session. Colour constants unchanged. Optional colour-spot check is not blocking. |
| QA-S1-05 | Info | **Accept as identity condition.** No implementation commit exists until the bounded commit below. |

No bounded remediation file list. Worktree left intact except for this decision file and permitted execution-index updates.

## Residual coverage (accepted, non-blocking)

Controlling WA-01/WA-02 verification lists are broader than the four-item Stage 1 P1 contract. Master does not treat these gaps as FAIL:

- Browser zoom 125% and keyboard access (WA-01 list)
- Azimuths 90/180/270, rapid edits, reload, both map backgrounds
- Dedicated WIFI-yellow live arrow
- CAP “Show selected sites on map”
- Production live JSON `errors[]` contains a `networkidle` timeout; QA narrative attributes a first-session timeout and a successful `wait_until=load` retry. Production fields are populated and screenshots exist. Accepted as record noise, not a product defect.

## What master re-ran vs accepted from QA

### Independently re-run by master (2026-09-08, this dirty tree @ HEAD `bc45b63`)

| Check | Result |
|---|---|
| `git status --short --branch`; `git rev-parse HEAD` | branch `codex/bl-006-ies-associations`; HEAD `bc45b63da41092175f7fbda97bc4c24f1f39bfe9`; dirty Stage 1 P1 tree preserved |
| `git merge-base --is-ancestor bc45b63 HEAD` | exit 0 |
| File-boundary vs work record | tracked product: `EngineeringMap.tsx`, `LightingPointLabels.tsx`, `LightingResultCard.tsx`, `globals.css` plus backlog note. Untracked scheduler/lib/tests + harness/QA. No `backend/`, `schemas/`, engines, `Input/`, lockfiles |
| `git diff --exit-code -- Input` | exit 0 |
| `git hash-object schemas/project.schema.json` vs `HEAD:` | identical `a9ededf2f4dc307140667c7d571fe3a41d8b7a6e` |
| Lockfiles | no diff (`backend/requirements.lock`, `frontend/pnpm-lock.yaml`) |
| `SOFTWARE_VERSION` | remains `0.7.0` |
| `harness/seals/` | `phase-06.md`, `phase-07.md`, `README.md` only; no Phase 8 |
| `scripts/validate_engineering_data.py` | PASS (7 catalogs; supplied-source hashes valid) |
| Frontend `corepack pnpm run typecheck` / `lint` / `build` / `test` | all exit 0; **70 passed**, 0 failed; build chunk-size advisory and unclassified-route note only |
| `git diff --check HEAD` on product paths | exit 0 |
| Fixture colours | LITE `#ef4444` / WIFI `#facc15` / SMART `#3b82f6` unchanged |
| Scheduler cancel-clears-id | confirmed in `map-frame-scheduler.mjs` |
| Live QA artifacts on disk | `harness/verify/2026-09-08-stage1-p1-independent-qa-live.json`, `-dev.json`; screenshots under `harness/tmp/stage1-p1-qa/screenshots/` including prod layout, arrows, labels, card, motion |
| Backend pytest | **not run** — live diff does not touch backend/schema/OpenAPI |

### Accepted from Independent QA without repeating the same command

| Check | Disposition |
|---|---|
| Isolated production `vinext start` and `vinext dev` MapLibre sessions | Accepted after inspecting live JSON (74-pole import, SHA `2f89f9f2…e328`, viewport/collapse/card/arrow/label probes) and confirming the screenshot set exists. Not re-launched by master (ports/tmp already used by QA). |
| Implementer `harness/verify/2026-09-08-stage1-p1-verification.md` | Historical/self-check only; not substituted for master commands |

### Not run by master

| Check | Disposition |
|---|---|
| Live Playwright / Vinext re-launch | **Not re-run.** Independent QA already executed genuine MapLibre on this dirty tree. Residual coverage above is accepted, not a new live matrix. |

## Commit authorization (yes) and required identity

**Commit: authorized.** **Merge: not authorized.** **Push: not authorized.**

The exact implementation identity required after commit is **the SHA of one new commit** on `codex/bl-006-ies-associations` that contains the reviewed dirty product/harness tree plus this decision file, and does **not** contain caches, `node_modules`, virtualenvs, `frontend/dist` / `.next` runtime output, `backend/data` runtime projects, or `harness/tmp/` screenshots.

Until that SHA exists, there is **no** accepted Stage 1 P1 implementation commit. After it exists, this CONDITIONAL PASS binds to that SHA only if the committed tree matches the reviewed set (no extra product files, no omitted required files). A follow-up identity confirmation (`git status` clean, `rev-parse HEAD`) is required before any later merge authorization. This decision does **not** itself perform that bind.

### Files authorized in that commit

Tracked modifications:

- `GOALS.md`, `PLANS.md` (execution-index; a one-line update citing this CONDITIONAL PASS is permitted)
- `docs/current-status.md` (current-gate sentence only; do not amend Phase 1–7 seals)
- `docs/post-roadmap-backlog.md`
- `frontend/app/globals.css`
- `frontend/app/components/EngineeringMap.tsx`
- `frontend/app/components/LightingPointLabels.tsx`
- `frontend/app/components/LightingResultCard.tsx`

Untracked product / tests:

- `frontend/app/lib/map-frame-scheduler.mjs`
- `frontend/app/lib/map-frame-scheduler.d.mts`
- `frontend/tests/map-frame-scheduler.test.mjs`
- `frontend/tests/workspace-layout.test.mjs`

Intake / contract (preserve, do not treat as engines):

- `docs/web-app-review-2026-09-08.md`
- `harness/verify/2026-09-08-web-audit-observations.json`

Harness / decision evidence:

- `harness/phases/2026-09-08-stage1-p1-display.md`
- `harness/logs/2026-09-08-stage1-p1-execution.md`
- `harness/verify/2026-09-08-stage1-p1-verification.md`
- `harness/verify/2026-09-08-stage1-p1-live.json`
- `harness/verify/2026-09-08-stage1-p1-independent-qa-review.md`
- `harness/verify/2026-09-08-stage1-p1-independent-qa-live.json`
- `harness/verify/2026-09-08-stage1-p1-independent-qa-dev.json`
- `harness/verify/run_stage1_p1_live.py`
- `harness/verify/run_stage1_p1_independent_qa_live.py`
- `docs/post-roadmap-stage1-p1-scoped-master-decision-2026-09-08.md` (this file)

Do **not** commit runtime projects, ad-hoc uploads, generated exports, caches, virtual environments, `node_modules`, or `harness/tmp/`. Do **not** modify `Input/`.

## Gate decision

| Question | Answer |
|---|---|
| Stage 1 P1 item set accepted | YES, with conditions above |
| Unconditional / sealed implementation commit | NO |
| Commit authorized | YES (bounded list; one commit) |
| Merge authorized | NO |
| Push authorized | NO |
| Stage 2+ authorized | NO |
| Phase 8 / harness seal authorized | NO |
| Engine / schema / `Input/` / lockfile changes authorized | NO |
| `verify_phase_readiness.py` used as item gate | NO |
| Phase 1–7 seals amended | NO |

## Exact next authorized action

**Create the single bounded implementation commit described above** on `codex/bl-006-ies-associations`, preserving the rest of the worktree (do not reset/clean/stash/revert). Record the new SHA. Do **not** merge. Do **not** push. Do **not** start Stage 2. Do **not** create `harness/seals/` entries.

After that commit, a separate identity-bind / merge authorization is required before `main`.
