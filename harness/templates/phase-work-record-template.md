# Phase work record — YYYY-MM-DD — Phase N

Status: draft / active / blocked / implementation complete awaiting QA / accepted

## Scope, authority, and non-goals

- Requested work:
- Controlling documents:
- Acceptance IDs governed by those documents:
- Authorized file boundary:
- Base commit and starting worktree status:
- Non-goals and later-phase exclusions:
- Durable goal identifier/state:
- Verifiable implementation stopping condition:

Do not copy requirements from the controlling contract. Link them and record only execution-specific interpretation or unresolved conflict.

## Environment and file-boundary preflight

| Preflight item | Evidence | Result | Required path/configuration | Authorized? |
|---|---|---|---|---|
| Runtime discovery |  | not run |  | unresolved |
| Locked dependency materialization |  | not run |  | unresolved |
| Build/test/lint/typecheck commands |  | not run |  | unresolved |
| Generated-artifact/validator commands |  | not run |  | unresolved |
| Browser/rendered-QA runtime and ports |  | not run |  | unresolved |

Product changes must not begin until every required supporting path is either inside the authorized boundary or covered by an explicit recorded amendment.

## Milestones

| Milestone | Contract reference | Expected evidence | Status |
|---|---|---|---|
|  |  |  | not started |

## Acceptance criteria

| Acceptance ID / criterion | Verification method | Evidence location | Status |
|---|---|---|---|
|  |  |  | not run |

## Changes and evidence

- Changed files:
- Decisions applied:
- Commands and durable evidence:

## Verification requirements

- Required deterministic commands:
- Required generated-artifact freshness checks:
- Required source/hash preservation checks:
- Required rendered or manual workflows:
- Required regression scope:

Record executions in a dated file made from `execution-log-template.md`; summarize the exact sealed commit in a verification record.

## Definition of Done

- [ ] All authorized milestones are complete.
- [ ] Every required acceptance item has objective PASS evidence.
- [ ] Every required deterministic command passed on the recorded commit/worktree.
- [ ] Source, prior-phase behavior, and file-boundary invariants are verified.
- [ ] Completion and rendered evidence reports are present if required.
- [ ] The implementation-readiness manifest passes on the recorded implementation commit and clean worktree.
- [ ] Independent QA handoff is recorded; QA itself remains pending.
- [ ] No later phase has begun.

Independent QA PASS, master PASS, and the phase seal belong to later gates and are not implementation-task Definition of Done items.

## Unknowns, conflicts, and blockers

- Unknown runtime inputs:
- Documentation conflicts:
- Blocked work / required direction:

## Recovery protocol

1. Preserve the current worktree and logs; do not reset or discard evidence.
2. Record the failed/interrupted command, exit state, affected files, and last verified milestone.
3. Inspect exact `HEAD`, status, and diff before resuming.
4. Revalidate any artifact that may be partial or stale.
5. Resume from the last verified milestone only within the authorized boundary; request direction if authority or requirements are unresolved.
6. Before declaring a blocker, make and log at least three materially different safe recovery attempts using the blocker template.
7. Continue other meaningful in-scope work while the affected command is recoverably unavailable.

## Non-blocking failures

Failing/missing tests, incomplete coverage/milestones, compiler/build/lint/typecheck failures, generated drift, runtime paths, occupied ports, temporary locks, caches, dependency materialization, dirty implementation files, missing reports, and normal response-turn boundaries require repair and continuation.

## Allowed stopping conditions

- The implementation-readiness verifier passes and the independent-QA handoff is recorded; or
- a completed blocker record proves three materially different recovery attempts failed, no meaningful in-scope work remains, and new authority, a product decision, external state, or prohibited scope expansion is required.

## Gate state

- Implementation:
- Durable goal:
- Implementation-readiness verifier:
- Independent QA:
- Master decision:
- Seal status:
