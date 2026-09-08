# Plans

This is the execution plan index. Phase 7 requirements, decisions, milestones, verification, and acceptance IDs remain in `harness/phases/phase-07.md`. Remediation history is governed by `docs/superpowers/plans/2026-09-05-phase-7-remediation.md`.

## Active plan

**Next action:** Independent QA of Stage 2. Contract and pasteable QA prompt: `docs/superpowers/plans/2026-09-08-stage2-bl-012-017-018.md`. Implementation commit `eb3a606`. Do not start Stage 3. Do not merge.

Post-roadmap item plan (not a numbered phase): `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md`. Stages 1–7 CONDITIONAL PASS: `docs/post-roadmap-bl-1-7-scoped-master-decision-2026-09-07.md` (commit `02c027ef`). BL-001 CONDITIONAL PASS: `docs/post-roadmap-bl-001-scoped-master-decision-2026-09-07.md`. Stage 1 P1 display CONDITIONAL PASS: `docs/post-roadmap-stage1-p1-scoped-master-decision-2026-09-08.md`. Provider: `docs/post-roadmap-bl-001-provider-authorization-2026-09-07.md`. Stage 0: `harness/phases/2026-09-07-stage-0-prep.md`. Stage 8: `harness/phases/2026-09-07-stage-8-bl-001-gated.md`.

Phase 7 remains formally closed by `docs/phase-7-master-gate-decision-2026-09-05.md` and `harness/seals/phase-07.md` (implementation `e24b6a1`; Independent QA PASS). Decisions `P7-D01` through `P7-D15` remain binding with amended `P7-D08`.

## Guardrails

- No source-pole creation, movement, redistribution, optimization, or deletion.
- No invented CAP operational values, RF predictions, compliance claims, or unsupported report claims.
- Ordinary failures enter the logged repair/retry loop and do not stop an authorized phase. Only a blocker proven under `AGENTS.md` may pause execution for user direction.
- Progress reports and response-turn boundaries do not end an unfinished durable goal.
- A Phase 7 seal is evidence of roadmap completion only and does not authorize Phase 8 or other post-roadmap work.

## Bootstrap record

The durable workflow bootstrap was created against clean main-branch commit `72441d2c` on 2026-08-30. Phase 6 was subsequently implemented at `3a81f316`, independently passed at `f9dcea2f`, and formally closed by the 2026-09-03 master gate and seal. Phase 7 remediation closed on 2026-09-05. The bootstrap record remains historical workflow evidence.
