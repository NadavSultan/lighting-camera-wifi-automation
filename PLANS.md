# Plans

This is the execution plan index. Phase 7 requirements, decisions, milestones, verification, and acceptance IDs remain in `harness/phases/phase-07.md`. Remediation history is governed by `docs/superpowers/plans/2026-09-05-phase-7-remediation.md`.

## Active plan

**Next gate:** BL-016 Independent QA returned FAIL with QA-01 on 2026-09-27. QA-01 correction is committed at `f542b164c136e8224e55867ea3f016a6987f7a44`; the scoped work record is `harness/phases/2026-09-27-bl-016-qa01-cors.md` and re-review handoff is `harness/verify/2026-09-27-bl-016-qa01-independent-qa-handoff.md`. Clean corrective readiness verification is pending. The new independent review must exercise the remaining interactive BL-016 Task 10 cases. BL-016 remains unaccepted. Stage 3 P2 remains accepted at `e5023ee`; BL-019/020, merge, push, Phase 8, and seals remain gated.

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
