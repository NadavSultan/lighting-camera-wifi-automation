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
8. `GOALS.md`
9. `PLANS.md`
10. `OPERATIONS.md`

Then read the active phase's controlling contract and gate records, inspect `git status --short --branch`, the exact `HEAD`, and the current diff, and preserve unrelated or user-owned changes. Phases 1-6 are accepted and formally closed. Phase 6 closed on 2026-09-03 after implementation readiness, independent QA PASS, master gate PASS, and a valid phase seal. Phase 7 planning decisions are approved; implementation remains unauthorized and gated.

## Durable execution workflow

Use `GOALS.md`, `PLANS.md`, and `OPERATIONS.md` as the repository's execution index. They record workflow state and verification procedure; the controlling product and phase requirements remain the existing documents they link to. Do not duplicate or silently supersede those documents.

Active-phase implementation is long-running work. When the execution environment provides a durable goal mechanism, the implementation session must create and activate one before changing product files. The goal must name one objective and one verifiable implementation-readiness stopping condition. Writing `/goal` or "do not stop" inside ordinary prose is not evidence that a durable goal exists. Record the goal state in the phase work record and execution log.

Keep launch prompts outcome-focused and short. Point to the repository contract, state the authorized action boundary, name the final readiness command, and define the proven-blocker rule once. Repository documents carry the detailed requirements. A progress report, completed response turn, partial pass, commit, or completion report is not a stopping event while the durable goal remains unfinished.

Before active-phase implementation, create a dated work record under `harness/phases/` from `harness/templates/phase-work-record-template.md`. It must link the controlling contract, state scope and non-goals, list milestones and acceptance IDs, define the authorized file boundary, and identify the exact base commit and starting diff. Do not copy or reinterpret the controlling requirements.

Before the file boundary is treated as final, run and record an environment preflight from the work-record template. It must test runtime discovery, locked dependency materialization, build/test/lint/typecheck entry points, generated-artifact commands, browser/runtime availability when required, and every supporting configuration file those commands may legitimately update. A missing required build-tool configuration path is a contract defect to resolve before implementation, not a surprise boundary expansion during the phase.

During execution, append exact command records from `harness/templates/execution-log-template.md` under `harness/logs/`. Before independent QA, create a verification summary under `harness/verify/`; independent QA must use `harness/templates/qa-review-template.md`. Never state that a command passed unless it was run against the recorded commit/worktree, exited successfully, and its result and warnings are preserved. Historical evidence must be labelled historical and cannot substitute for current deterministic verification.

If work is interrupted or a command fails, preserve the worktree, inspect status/diff and the last verified milestone, record the failure and affected artifacts, and resume only from that evidence. Never discard, overwrite, auto-resolve, or rerun a destructive step to recover.

Failing tests, missing tests, incomplete acceptance coverage, incomplete milestones, compiler/lint/typecheck/build failures, missing generated output, temporary process/cache/file locks, occupied local ports, runtime `PATH` problems, recoverable dependency installation, dirty implementation files, absent reports, and the end of a normal response turn are not stopping conditions. Diagnose, repair, rerun, and continue. If one condition appears blocking, make and log at least three materially different safe recovery attempts before requesting direction. A blocker is valid only when the same condition still prevents meaningful in-scope progress and requires new authority, a product decision, an external-state change, or a prohibited scope expansion. Use `harness/templates/blocker-record-template.md`; vague blocker summaries are invalid.

Stop and request direction only when the proven-blocker rule is satisfied for unresolved authority, requirements, source precedence, file boundary, source preservation, or a required product decision; when continuing would enter a gated phase; or when required verification cannot be completed truthfully after safe in-scope recovery is exhausted. Otherwise record the checkpoint and continue the durable goal.

Implementation readiness is separate from phase acceptance. Before implementation handoff, complete `harness/templates/implementation-readiness-template.json` and run `harness/verify/verify_phase_readiness.py`. The verifier must pass against the recorded implementation commit and a clean worktree. It does not create a phase seal and cannot replace independent QA or the master gate.

A phase is not complete merely because implementation is committed or a completion report exists. A seal under `harness/seals/` is valid only when created from `harness/templates/phase-seal-template.md` after all contract-required deterministic checks pass on the sealed commit, every required acceptance item has objective evidence, independent QA records PASS, and the master gate decision records PASS. Any missing, failed, skipped, stale, or unverified required check makes the seal invalid. A seal is evidence only; it never authorizes the next phase.

## Safety and engineering rules

- Existing-pole mode is the default. Never generate, redistribute, optimize, move, or delete customer poles without explicit user authorization.
- Keep every uploaded source file byte-for-byte unchanged. Store source data, user edits, calculated data, and recommendations separately.
- Treat WGS84 coordinates as interchange/display data only. Select a local projected CRS in metres for distance, area, coverage, or later photometric calculations.
- Do not infer CAP limits, fixture applicability, photometric conventions, or analytics performance. Record an assumption or block the feature.
- Camera downward angle is measured below horizontal: 0 degrees is horizontal and 90 degrees is vertically down.
- Phase work must remain gated. Phases 1-6 are closed. All Phase 7 planning decisions are approved, but implementation requires separate explicit authorization.

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

Phase 2 adds operational fixture-model, IES, and camera/lens catalogs; Phase 3 adds fixed-mount camera geometry; Phase 4 adds the accepted simplified direct-lighting engine; Phase 5 adds accepted conceptual Wi-Fi geometry; Phase 6 adds accepted CAP / JNET1 distance-graph and constraint planning. The seven approved Phase 1 engineering catalogs remain frozen at `1.0.0`. Do not plan or implement Phase 7 reporting or any later calculation/recommendation engine without separate explicit authorization.
