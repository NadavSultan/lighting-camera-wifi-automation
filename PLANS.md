# Plans

This is the execution plan index. Phase 7 requirements, decisions, milestones, verification, and acceptance IDs remain in `harness/phases/phase-07.md`. Remediation history is governed by `docs/superpowers/plans/2026-09-05-phase-7-remediation.md`.

## Active plan

No active gated phase plan. Phase 7 is formally closed by `docs/phase-7-master-gate-decision-2026-09-05.md` and `harness/seals/phase-07.md` (implementation `e24b6a1`; Independent QA PASS). Decisions `P7-D01` through `P7-D15` remain binding with amended `P7-D08`. Post-roadmap work requires separate authorization.

## Guardrails

- No source-pole creation, movement, redistribution, optimization, or deletion.
- No invented CAP operational values, RF predictions, compliance claims, or unsupported report claims.
- Ordinary failures enter the logged repair/retry loop and do not stop an authorized phase. Only a blocker proven under `AGENTS.md` may pause execution for user direction.
- Progress reports and response-turn boundaries do not end an unfinished durable goal.
- A Phase 7 seal is evidence of roadmap completion only and does not authorize Phase 8 or other post-roadmap work.

## Bootstrap record

The durable workflow bootstrap was created against clean main-branch commit `72441d2c` on 2026-08-30. Phase 6 was subsequently implemented at `3a81f316`, independently passed at `f9dcea2f`, and formally closed by the 2026-09-03 master gate and seal. Phase 7 remediation closed on 2026-09-05. The bootstrap record remains historical workflow evidence.
