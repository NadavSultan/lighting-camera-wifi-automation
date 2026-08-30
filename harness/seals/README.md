# Acceptance seals

Create a seal only from `../templates/phase-seal-template.md`. A seal is valid only when every contract-required deterministic command passed on the exact sealed commit, every acceptance item has objective evidence, independent QA records PASS, and the master gate decision records PASS. Missing, skipped, failed, stale, or unrecorded required verification invalidates the seal.

A seal must cite immutable repository evidence and must not claim authorization, replace a gate decision, or authorize the next phase. Implementation completion reports alone are never seal evidence.
