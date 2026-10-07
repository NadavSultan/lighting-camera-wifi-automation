# Plans

This is the execution plan index. Phase 7 requirements, decisions, milestones, verification, and acceptance IDs remain in `harness/phases/phase-07.md`. Remediation history is governed by `docs/superpowers/plans/2026-09-05-phase-7-remediation.md`.

## Active plan

The separately approved 2026-10-04 camera range/lens/distance UX plan is complete at product `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`; independent QA PASS and scoped master PASS are recorded in `harness/verify/2026-10-04-camera-range-lens-distance-independent-qa.md` and `docs/2026-10-07-camera-range-lens-distance-scoped-master-gate.md`. No active post-roadmap implementation plan, merge, push, seal, or Phase 8 is authorized.

**Prior accepted gate:** BL-016 / WA-09 received Independent QA PASS and scoped master PASS on 2026-09-30 for product commit `5656da55`. The gate record is `docs/bl-016-scoped-master-gate-decision-2026-09-30.md`; the independent report is `harness/verify/2026-09-30-bl-016-qa03-ia01-independent-qa.md`. That earlier accepted product requires no further retest; the later camera UX received its separate QA and master gates on 2026-10-04 and 2026-10-07. Stage 3 P2 remains accepted at `e5023ee`. Integration/push and BL-019/BL-020 or other later work require separate authorization; no Phase 8 or seal is created.

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
