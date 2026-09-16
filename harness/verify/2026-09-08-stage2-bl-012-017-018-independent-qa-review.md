# Independent QA review — 2026-09-16 — Stage 2 BL-012 / BL-017 / BL-018

Verdict: **PASS**

## Scope, independence, and non-goals

- Exact implementation reviewed: product commit `eb3a606253d794bf8ef685eb69d6c885368823ea`; checkout `a0cf9ceae6f5097a12a858592b2ec249d988587c` adds documentation only.
- Base: `2f0f4a9c42a3a7bdbb51971591aaced5c57a8d38`; both required ancestry checks exited 0.
- Controlling contract: `docs/superpowers/plans/2026-09-08-stage2-bl-012-017-018.md`; WA-05, WA-10, WA-11.
- Reviewer independence: this session did not implement the Stage 2 product work and treated implementer records as claims only.
- Scope: BL-012, BL-017, BL-018 only. No product fixes, merge, push, Stage 3, seal, or commit.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | identity, ancestry, complete Stage 2 diff, protected paths | PASS |
| Deterministic verification | typecheck, lint, 78 tests, production build | PASS |
| Acceptance-matrix review | independent disposition for all three items | PASS |
| Rendered/manual workflow | isolated production UI and isolated FastAPI store | PASS |
| Source/prior-phase regression review | `Input/`, KML hash, forbidden-scope scan | PASS |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| BL-012 / WA-05 | source/coordinate-chain review; helper/clamp tests; isolated production browser matrix | `2026-09-16-stage2-bl-012-017-018-independent-qa-live.json`; screenshots under `harness/tmp/stage2-independent-qa/screenshots/`; execution log | **PASS** — all four corners and center remained inside the map. Center offset was `(12.00, 11.985)` px; right/bottom cases clamped as required. Drag moved the card, Reset returned exactly to the measured anchor, pan/zoom and panel collapse/restore repositioned the anchored card inside the map, and no card/drag position key appeared in project JSON. |
| BL-017 / WA-10 | formatter and wiring review; exact-value unit tests | 78-test run covers `0`, `null`, threshold, ordinary values and WA-10 tiny inputs; source review confirms raw stored lux remains on label objects and ratios read stored numeric fields | **PASS** |
| BL-018 / WA-11 | isolated 74-pole import; direct browser inspection; CSS/source and tests | default Lighting tab independently observed; four tabs and toolbar Report Package present; CAP required inputs remain in an open expandable details block; draft state is not cleared by tab setters; viewport/overflow tests and source review | **PASS** |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `corepack pnpm run typecheck` | `a0cf9ce` / product `eb3a606` | 0 | fresh |
| `corepack pnpm run lint` | same | 0 | fresh |
| `corepack pnpm run test` | same | 0, 78/78 | fresh |
| `corepack pnpm run build` | same | 0 | advisory only |
| isolated production build for API `:8039` | same | 0 | fresh |
| `git diff --exit-code -- Input` | same | 0 | source unchanged |
| Miracle Mile SHA-256 | same | match | 74-pole source identity |
| Isolated API/store + Vinext browser matrix | same | 0 / PASS | HTTP 200; 74 poles; five anchor positions, motion, collapse/restore, drag/Reset, JSON persistence check; no harness errors |

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| S2-QA-01 | Closed | WA-05 browser measurements at four corners and center plus motion/collapse/drag/Reset | **Closed by passing independent rendered retest.** Five-position containment, ~12 px center offset, clamping, pan/zoom, panel collapse/restore, drag, exact Reset, and session-only JSON behavior are recorded in the live JSON and screenshots. | None. |
| S2-QA-02 | Info | clean diff hygiene | `git diff --check 2f0f4a9..eb3a606` reports two trailing-space lines in the Stage 2 plan. | Optional documentation cleanup in an authorized evidence/remediation session. |

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [x] Every mandatory acceptance item disposed as PASS or a blocking finding.
- [x] Required deterministic checks completed on the reviewed product tree.
- [x] Source preservation and later-stage exclusion verified.
- [x] Verdict does not rely on implementer claims.

## Verdict and next gate

- Verdict: **PASS** (BL-012 PASS; BL-017 PASS; BL-018 PASS).
- Open findings: `S2-QA-02` Info only; `S2-QA-01` is closed.
- Master gate eligibility: **YES for scoped Stage 2 master review only**. This QA PASS does not authorize merge, push, Stage 3, or a seal.
- Exact next action: scoped Stage 2 master review on product commit `eb3a606` / documentation-only descendant. Merge, push, Stage 3, and seals remain unauthorized.
