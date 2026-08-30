# Execution log — YYYY-MM-DD — Phase N

## Scope and non-goals

- Phase work record:
- Controlling contract and acceptance IDs:
- Authorized work/milestone:
- Non-goals and excluded phases:
- Exact starting commit/worktree:
- Durable goal identifier/state:
- Implementation-readiness manifest:

## Environment and file-boundary preflight

| Check | Exact command/inspection | Result | Repository paths affected or required | Boundary disposition |
|---|---|---|---|---|
| Runtime discovery |  | not run |  | unresolved |
| Locked dependency materialization |  | not run |  | unresolved |
| Build/test/lint/typecheck entry points |  | not run |  | unresolved |
| Generated-artifact/validator entry points |  | not run |  | unresolved |
| Browser/local-server/port requirements |  | not run |  | unresolved |

## Milestone and acceptance criteria

- Milestone being executed:
- Objective completion condition:
- Evidence required:

## Execution entries

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
|  |  |  | not run |  |  |

Do not write PASS unless the exact command/action completed successfully for the recorded worktree. Label copied or prior evidence as historical.

## Verification requirements

- Deterministic checks required for this milestone:
- Source/hash/generated-artifact checks:
- Rendered/manual checks:
- Checks not run and reason:

## Definition of Done

- [ ] The milestone's acceptance criteria have objective evidence.
- [ ] Required checks passed on the recorded commit/worktree.
- [ ] Changed files remain within the authorized boundary.
- [ ] No source, prior-phase, dependency, migration, or later-phase violation occurred.

## Recovery protocol

1. Preserve the worktree and this log after failure/interruption.
2. Record exit state, partial artifacts, and the last verified entry.
3. Inspect `HEAD`, status, and diff before retrying.
4. Revalidate partial/stale artifacts and resume from the last verified state only.
5. Make and log at least three materially different safe recovery attempts before classifying the same condition as a blocker.
6. Continue with other meaningful in-scope work while one command is recoverably unavailable.

## Non-blocking failures

Failing or missing tests, incomplete acceptance coverage or milestones, build/lint/typecheck/compiler failures, generated drift, runtime `PATH` issues, occupied ports, temporary locks, caches, recoverable dependency installation, dirty implementation files, missing reports, and a response-turn boundary require repair and continuation. They do not justify a final stop.

## Allowed stopping conditions

- The complete implementation-readiness verifier passes and the independent-QA handoff is recorded; or
- a blocker record proves three materially different safe recovery attempts failed, no meaningful in-scope progress remains possible, and new authority, a product decision, external state, or prohibited scope expansion is required.

Completing one milestone is a checkpoint, not a stopping condition when later authorized milestones remain.

## Close state

- Last verified milestone/state:
- Open blockers:
- Blocker record, if any:
- Recovery-attempt count:
- Durable goal state:
- Implementation-readiness verifier result:
- Next authorized action:
