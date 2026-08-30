# Independent QA review — YYYY-MM-DD — Phase N

Verdict: NOT REVIEWED / PASS / FAIL / BLOCKED

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed:
- Controlling contract, phase record, and acceptance IDs:
- Reviewer/session independence:
- Review scope:
- Non-goals and excluded phases:

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review |  | not run |
| Deterministic verification |  | not run |
| Acceptance-matrix review |  | not run |
| Rendered/manual workflow |  | not run |
| Source/prior-phase regression review |  | not run |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
|  |  |  | not run |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
|  |  | not run |  |

Historical implementation evidence may guide selection but cannot replace required independent current-commit checks.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
|  |  |  |  |  |

## Definition of Done

- [ ] Complete implementation diff and file boundary reviewed.
- [ ] Every mandatory acceptance item independently disposed as PASS or recorded as a blocking finding.
- [ ] Required deterministic and rendered checks completed on the exact reviewed commit.
- [ ] Source preservation, migration, prior-phase regressions, and later-phase exclusion verified.
- [ ] Verdict is supported without relying on unverified claims.

## Recovery protocol

1. Preserve QA evidence and the exact reviewed commit identity.
2. Record failed/interrupted checks and whether implementation changed afterward.
3. If implementation changes, invalidate affected QA results and retest the new exact commit.
4. Resume only from evidence that remains applicable.

## Allowed stopping conditions

- The reviewed commit changes or cannot be identified.
- Required evidence/runtime is unavailable and no truthful disposition is possible.
- A Critical/Major safety, authorization, source-preservation, or phase-boundary issue requires correction first.
- QA is complete and the supported PASS/FAIL verdict is recorded. QA never authorizes the next phase.

## Verdict and next gate

- Verdict:
- Open findings:
- Master gate eligibility:
- Exact next action:
