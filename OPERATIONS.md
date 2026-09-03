# Operations

## Source of truth and records

Read the startup sequence in `AGENTS.md`. Use `docs/current-status.md` for current phase state and the accepted Phase 6 contract for Phase 6 behaviour. Place phase work records in `harness/phases/`, command logs in `harness/logs/`, verification summaries in `harness/verify/`, and only completed gate seals in `harness/seals/`.

Known documentation conflict: `README.md` still describes a Phase 4 application and says Wi-Fi/CAP are not calculated. `docs/current-status.md`, the implementation plan, source tree, and recent Phase 5 gate evidence show Phase 5 is closed. Treat the dated status/gate records as controlling until the README is deliberately refreshed.

Historical wording in section 16 of the Phase 6 planning contract says its policy decisions alone did not authorize implementation. The later, explicit implementation authorization is recorded by the contract's current status/authorization boundary and `docs/decision-log.md` DL-016. Do not erase that chronology or misread the earlier sentence as the current gate.

## Repository commands

These commands are the canonical repository checks discovered from `backend/pyproject.toml`, `frontend/package.json`, `README.md`, and the approved Phase 6 implementation prompt. Use the repository's configured Python 3.12 environment; the `.venv` paths below are the documented project form, not evidence that a virtual environment exists in every checkout.

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider

Set-Location ..
.\.venv\Scripts\python.exe .\scripts\validate_engineering_data.py

Set-Location .\backend
..\.venv\Scripts\python.exe .\scripts\export_schema.py
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider

Set-Location ..\frontend
pnpm run test
pnpm run typecheck
pnpm run lint
pnpm run build

Set-Location ..
git diff --check
git status --short
```

The frontend package also provides `pnpm run dev`, `pnpm run start`, and `pnpm run db:generate`. The latter is not a standard verification command and must not be run without separately authorized migration work.

## Baseline verification

Date: 2026-08-30 workflow review

- Worktree before bootstrap: clean (`git status --short` produced no entries).
- CI configuration: none found (`.github/` is absent).
- Backend full suite: **PASS** on current commit `72441d2c` using the bundled Python 3.12 runtime (137 tests; one known Starlette/httpx deprecation warning).
- Engineering-data/source validation: **PASS**; seven catalog/schema pairs and all supplied-source hashes validated.
- Generated project schema/OpenAPI freshness: **PASS through the current backend freshness test**. The write-producing export command was not run during this documentation-only review.
- Frontend test/typecheck/lint/build: **not run**. This checkout has no `frontend/node_modules`; the attempted `pnpm run test` stopped before the test script because dependency materialization required unavailable registry access. No frontend pass is claimed.
- Exact commands and limitations are recorded in `harness/verify/2026-08-30-workflow-review.md`. Existing historical results in `docs/current-status.md` remain historical, not substitutes for this baseline.

## Recording rules

- Name records with ISO date and phase, for example `2026-08-30-phase-6-implementation.md`.
- Include exact commands, exit codes, commit/working-tree identity, warnings, and whether the result is current or historical.
- Use the phase, execution-log, verification, QA, and seal templates in `harness/templates/`; link controlling requirements instead of duplicating them.
- Never create a seal for a merely authorized or implemented phase. A valid seal requires all deterministic contract checks on the sealed commit, complete acceptance evidence, independent QA PASS, and master PASS. A skipped, failed, stale, or unrecorded required check makes the seal invalid.

## Durable implementation protocol

Use `harness/templates/execution-launch-template.md` to start implementation. The session must activate a real durable goal when the environment supports it and record the goal identifier/state. An instruction that merely contains the characters `/goal` is not sufficient. The launch message should link the phase contract rather than repeat it.

The implementation loop is:

1. recover exact worktree and evidence state;
2. complete environment and file-boundary preflight;
3. execute the first incomplete milestone;
4. run its exact verification;
5. repair failures and rerun;
6. update the execution log and work record;
7. continue immediately to the next incomplete milestone;
8. complete final deterministic and rendered verification;
9. pass the implementation-readiness verifier;
10. hand off to independent QA without creating a phase seal.

A compact progress message may report the current milestone, verified evidence, remaining work, and blocker state. It must not end an unfinished goal.

## Environment and boundary preflight

Before implementation changes, record the following in the phase work record:

- exact Git base, branch/worktree, starting diff, and user-owned changes;
- Python, Node, package-manager, browser, and other required runtime discovery;
- locked dependency installation or an exact reason it cannot yet run;
- build, test, lint, typecheck, schema-generation, validator, and local-server entry-point discovery;
- ports, environment variables, writable runtime/cache locations, and browser access needed by rendered QA;
- every repository configuration or generated file that a required command may update;
- confirmation that the authorized boundary includes those legitimate paths, or an explicit pre-implementation amendment.

Do not lock a phase contract around commands that have never been checked in a clean representative worktree unless the limitation and required setup are explicit.

## Failure and blocker classification

Ordinary repair work includes failing/missing tests, incomplete milestones or acceptance coverage, build/lint/typecheck/compiler errors, generated-file drift, runtime path problems, occupied ports, temporary locks, cache cleanup, recoverable dependency installation, dirty implementation files, and missing evidence reports. These conditions must be diagnosed and repaired; they are not reasons to return a final answer.

Before claiming a blocker, create a record from `harness/templates/blocker-record-template.md` and document at least three materially different safe recovery attempts. The record must show why no meaningful in-scope work can continue and identify the exact new authority, product decision, external-state change, or scope expansion required. If that showing cannot be made, the session continues.

## Phase 6 pnpm boundary correction — 2026-08-30

The user explicitly resolved the Phase 6 frontend dependency-materialization boundary defect in `docs/decision-log.md` DL-017. `frontend/pnpm-workspace.yaml` is authorized only for `allowBuilds` values `esbuild: true`, `sharp: false`, and `workerd: false` against the existing locked dependency graph. Dependency additions, removals, upgrades, lockfile changes, and unrelated workspace-policy changes remain unauthorized.

The earlier pnpm-boundary interruption in the separate Phase 6 execution worktree is therefore stale and must not remain an open blocker. Execution must retain its historical command evidence, mark the authority issue resolved, remove any false claim that M6-M9 are blocked by the file boundary, and resume at the first incomplete milestone. Acceptance-selector depth remains ordinary incomplete implementation/test work, not a stopping condition.

## Implementation-readiness check

Copy `harness/templates/implementation-readiness-template.json` to a phase-specific manifest under `harness/verify/`, complete every required row, and run:

```powershell
python harness/verify/verify_phase_readiness.py --manifest harness/verify/phase-XX-readiness.json
```

The verifier checks the goal state, milestone and acceptance dispositions, exact command evidence, deterministic/rendered/source/boundary checks, required reports, blocker state, implementation commit ancestry, evidence-only commits after that implementation commit, worktree cleanliness, and absence of a premature phase seal. Its PASS means only **implementation complete awaiting independent QA**.

## Current Phase 6 reconciliation evidence

Phase 6 implementation is `3a81f31682c333928879ecb5168183f1f950ac1d`; evidence-only history reaches independent-QA commit `f9dcea2fcc9bd8fc4a5118793a383736e5d72695`. The readiness verifier passed all 10 milestones and 30 acceptance IDs. Independent QA passed the full deterministic and genuine production 74-pole workflow with no findings. The 2026-09-03 master gate reran the backend suite before and after schema generation using isolated pytest temp paths, the engineering/source validator, frontend production build, 15 rendered tests, strict TypeScript, ESLint, diff/source checks, and readiness verification; all passed. The initial master backend attempt hit only a Windows permission error in the shared pytest temp root and was replaced by the recorded isolated-temp reruns. `docs/phase-6-master-gate-decision-2026-09-03.md` and `harness/seals/phase-06.md` close Phase 6.

## Current Phase 7 planning state

The user authorized Phase 7 planning and then explicitly approved every decision `P7-D01` through `P7-D15` on 2026-09-03. `harness/phases/phase-07.md` is the binding planning contract and DL-018 records the approval. Phase 7 implementation, dependencies, versions/schema changes, and report generation remain unauthorized until a separate explicit implementation authorization.
