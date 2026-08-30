# Durable phase implementation launch

Use this as the short launch message for an approved implementation phase. Replace every placeholder. Detailed requirements stay in the repository contract.

```text
Create and activate a durable goal using the environment's real goal mechanism:

Complete the approved implementation contract in `harness/phases/phase-XX.md`.
Continue across turns until `harness/verify/verify_phase_readiness.py` passes
for the phase manifest and the independent-QA handoff is recorded.

Read `AGENTS.md` and its required startup sequence, then the phase contract,
current work record/logs, source/tests, and exact Git state. Recover from the
first incomplete milestone. Do not repeat verified work unless its inputs changed.

You are authorized to make all non-destructive local changes inside the contract's
file boundary, run its dependencies/build/tests/servers/browser workflow, repair
failures, clean generated caches, and commit implementation/evidence. Do not ask
for routine confirmation between milestones.

Failing or missing tests, incomplete coverage/milestones, build/lint/typecheck
errors, generated drift, runtime paths, ports, temporary locks, caches, dependency
materialization, dirty implementation files, missing reports, and response-turn
boundaries are repair work, not blockers. Record progress and continue.

Stop early only when a blocker record proves three materially different safe
recovery attempts failed, no meaningful in-scope work remains possible, and the
exact new authority, product decision, external-state change, or prohibited scope
expansion is identified. Otherwise continue the durable goal.

Implementation completion does not accept or seal the phase. End only with the
passing readiness manifest and independent-QA handoff, or a proven blocker.
```

The task creator must verify that a real goal was activated. Merely including `/goal` in prose is not sufficient.
