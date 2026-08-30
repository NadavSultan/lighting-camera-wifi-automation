"""Fail closed unless a phase implementation is ready for independent QA."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REQUIRED_CHECK_IDS = {
    "final_verification",
    "generated_artifact_freshness",
    "source_preservation",
    "file_boundary",
    "rendered_workflow",
    "regression",
}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
PHASE_RE = re.compile(r"^[0-9]+$")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def repo_path(repo: Path, raw: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(raw, str) or not raw or raw == "REPLACE":
        errors.append(f"{label}: repository-relative evidence path is required")
        return None
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        errors.append(f"{label}: path must stay repository-relative: {raw!r}")
        return None
    resolved = (repo / candidate).resolve()
    try:
        resolved.relative_to(repo.resolve())
    except ValueError:
        errors.append(f"{label}: path escapes repository: {raw!r}")
        return None
    if not resolved.is_file():
        errors.append(f"{label}: evidence file does not exist: {raw!r}")
        return None
    return resolved


def evidence_list(repo: Path, raw: Any, label: str, errors: list[str]) -> None:
    if not isinstance(raw, list) or not raw:
        errors.append(f"{label}: at least one evidence file is required")
        return
    for index, item in enumerate(raw):
        repo_path(repo, item, f"{label}[{index}]", errors)


def indexed_rows(
    repo: Path,
    raw: Any,
    label: str,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        errors.append(f"{label}: non-empty list is required")
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}]: object is required")
            continue
        row_id = item.get("id")
        if not isinstance(row_id, str) or not row_id:
            errors.append(f"{label}[{index}].id: non-empty string is required")
            continue
        if row_id in rows:
            errors.append(f"{label}: duplicate id {row_id!r}")
            continue
        rows[row_id] = item
        if item.get("status") != "PASS":
            errors.append(f"{label}.{row_id}: status must be PASS")
        evidence_list(repo, item.get("evidence"), f"{label}.{row_id}.evidence", errors)
    return rows


def expected_ids(raw: Any, label: str, errors: list[str]) -> set[str]:
    if not isinstance(raw, list) or not raw or not all(isinstance(item, str) and item for item in raw):
        errors.append(f"{label}: non-empty string list is required")
        return set()
    values = set(raw)
    if len(values) != len(raw):
        errors.append(f"{label}: duplicate ids are not allowed")
    return values


def normalize_prefix(raw: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(raw, str) or not raw:
        errors.append(f"{label}: non-empty repository-relative prefix is required")
        return None
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"{label}: prefix must stay repository-relative: {raw!r}")
        return None
    return raw.replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Repository-relative or absolute readiness manifest")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = repo / manifest_path
    errors: list[str] = []

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"READINESS FAIL: cannot read manifest: {exc}", file=sys.stderr)
        return 1
    if not isinstance(manifest, dict):
        print("READINESS FAIL: manifest root must be an object", file=sys.stderr)
        return 1

    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    phase = manifest.get("phase")
    if not isinstance(phase, str) or not PHASE_RE.fullmatch(phase):
        errors.append("phase must contain digits only")

    goal = manifest.get("goal")
    if not isinstance(goal, dict):
        errors.append("goal object is required")
    else:
        if not isinstance(goal.get("objective"), str) or goal.get("objective") in {"", "REPLACE"}:
            errors.append("goal.objective must be concrete")
        if goal.get("status") != "ACHIEVED":
            errors.append("goal.status must be ACHIEVED")
        if not isinstance(goal.get("stopping_condition"), str) or goal.get("stopping_condition") in {"", "REPLACE"}:
            errors.append("goal.stopping_condition must be concrete")

    implementation_commit = manifest.get("implementation_commit")
    if not isinstance(implementation_commit, str) or not COMMIT_RE.fullmatch(implementation_commit) or set(implementation_commit) == {"0"}:
        errors.append("implementation_commit must be a non-zero 40-character lowercase Git commit")
    else:
        commit_check = git(repo, "cat-file", "-e", f"{implementation_commit}^{{commit}}")
        if commit_check.returncode != 0:
            errors.append("implementation_commit does not resolve to a commit")
        ancestor = git(repo, "merge-base", "--is-ancestor", implementation_commit, "HEAD")
        if ancestor.returncode != 0:
            errors.append("implementation_commit must be HEAD or an ancestor of HEAD")

    expected_milestones = expected_ids(manifest.get("expected_milestone_ids"), "expected_milestone_ids", errors)
    milestones = indexed_rows(repo, manifest.get("milestones"), "milestones", errors)
    if expected_milestones and set(milestones) != expected_milestones:
        errors.append("milestones must exactly match expected_milestone_ids")

    expected_acceptance = expected_ids(manifest.get("expected_acceptance_ids"), "expected_acceptance_ids", errors)
    acceptance = indexed_rows(repo, manifest.get("acceptance_criteria"), "acceptance_criteria", errors)
    if expected_acceptance and set(acceptance) != expected_acceptance:
        errors.append("acceptance_criteria must exactly match expected_acceptance_ids")

    commands = manifest.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append("commands: non-empty list is required")
    else:
        command_ids: set[str] = set()
        for index, command in enumerate(commands):
            label = f"commands[{index}]"
            if not isinstance(command, dict):
                errors.append(f"{label}: object is required")
                continue
            command_id = command.get("id")
            if not isinstance(command_id, str) or not command_id:
                errors.append(f"{label}.id: non-empty string is required")
            elif command_id in command_ids:
                errors.append(f"commands: duplicate id {command_id!r}")
            else:
                command_ids.add(command_id)
            if not isinstance(command.get("command"), str) or command.get("command") in {"", "REPLACE"}:
                errors.append(f"{label}.command: exact command is required")
            if command.get("ran") is not True or command.get("exit_code") != 0:
                errors.append(f"{label}: command must have ran=true and exit_code=0")
            if command.get("tested_commit") != implementation_commit:
                errors.append(f"{label}.tested_commit must equal implementation_commit")
            evidence_list(repo, command.get("evidence"), f"{label}.evidence", errors)

    checks = indexed_rows(repo, manifest.get("required_checks"), "required_checks", errors)
    if set(checks) != REQUIRED_CHECK_IDS:
        errors.append("required_checks must contain exactly: " + ", ".join(sorted(REQUIRED_CHECK_IDS)))

    reports = manifest.get("reports")
    required_reports = {
        "phase_work_record",
        "execution_log",
        "verification_summary",
        "completion_report",
        "rendered_evidence",
    }
    if not isinstance(reports, dict) or set(reports) != required_reports:
        errors.append("reports must contain exactly: " + ", ".join(sorted(required_reports)))
    else:
        for name, path in reports.items():
            repo_path(repo, path, f"reports.{name}", errors)

    blockers = manifest.get("blockers")
    if blockers != []:
        errors.append("blockers must be an empty list for implementation readiness")

    gate = manifest.get("gate")
    expected_gate = {
        "implementation": "IMPLEMENTATION_COMPLETE_AWAITING_QA",
        "independent_qa": "PENDING",
        "master": "PENDING",
        "phase_seal": "ABSENT",
    }
    if gate != expected_gate:
        errors.append(f"gate must equal {expected_gate!r}")

    prefixes_raw = manifest.get("allowed_evidence_paths_after_implementation_commit")
    prefixes: list[str] = []
    if not isinstance(prefixes_raw, list) or not prefixes_raw:
        errors.append("allowed_evidence_paths_after_implementation_commit must be non-empty")
    else:
        for index, raw in enumerate(prefixes_raw):
            prefix = normalize_prefix(raw, f"allowed_evidence_paths_after_implementation_commit[{index}]", errors)
            if prefix is not None:
                prefixes.append(prefix)

    if isinstance(implementation_commit, str) and COMMIT_RE.fullmatch(implementation_commit):
        changed = git(repo, "diff", "--name-only", f"{implementation_commit}..HEAD")
        if changed.returncode != 0:
            errors.append("could not inspect evidence-only commits after implementation_commit")
        elif prefixes:
            for raw_path in changed.stdout.splitlines():
                normalized = raw_path.replace("\\", "/")
                if not any(normalized.startswith(prefix) for prefix in prefixes):
                    errors.append(
                        "non-evidence path changed after implementation_commit: " + normalized
                    )

    status = git(repo, "status", "--porcelain")
    if status.returncode != 0:
        errors.append("could not inspect worktree cleanliness")
    elif status.stdout.strip():
        errors.append("worktree must be clean; current status:\n" + status.stdout.rstrip())

    if isinstance(phase, str) and PHASE_RE.fullmatch(phase):
        phase_number = str(int(phase))
        seal_candidates = {
            repo / "harness" / "seals" / f"phase-{phase}.md",
            repo / "harness" / "seals" / f"phase-{phase_number}.md",
            repo / "harness" / "seals" / f"phase-{int(phase):02d}.md",
        }
        for seal in seal_candidates:
            if seal.is_file():
                errors.append(f"premature phase seal exists: {seal.relative_to(repo)}")

    if errors:
        print("IMPLEMENTATION READINESS: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("IMPLEMENTATION READINESS: PASS")
    print(f"phase={phase}")
    print(f"implementation_commit={implementation_commit}")
    print(f"milestones={len(milestones)}")
    print(f"acceptance_criteria={len(acceptance)}")
    print("gate=implementation complete awaiting independent QA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
