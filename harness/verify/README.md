# Verification summaries

Create dated summaries from `../templates/verification-summary-template.md`. Distinguish commands run on the current worktree from historical evidence and record commands that were intentionally not run.

For implementation handoff, copy `../templates/implementation-readiness-template.json` to `phase-XX-readiness.json`, complete it, and run `verify_phase_readiness.py --manifest phase-XX-readiness.json` from this directory or pass the repository-relative path from the root. A PASS establishes only implementation readiness for independent QA; it never creates a phase seal.
