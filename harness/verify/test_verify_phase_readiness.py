from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("verify_phase_readiness.py")


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


class ReadinessVerifierTests(unittest.TestCase):
    def create_ready_repo(self, root: Path) -> Path:
        (root / "harness" / "verify").mkdir(parents=True)
        shutil.copy2(SCRIPT, root / "harness" / "verify" / SCRIPT.name)
        (root / "product.txt").write_text("implementation\n", encoding="utf-8")
        run("git", "init", "-q", cwd=root)
        run("git", "config", "user.email", "readiness-test@example.invalid", cwd=root)
        run("git", "config", "user.name", "Readiness Test", cwd=root)
        run("git", "add", ".", cwd=root)
        run("git", "commit", "-q", "-m", "implementation", cwd=root)
        implementation_commit = run("git", "rev-parse", "HEAD", cwd=root).stdout.strip()

        evidence = "harness/phase-99-evidence.md"
        (root / evidence).write_text("verified evidence\n", encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "phase": "99",
            "goal": {
                "objective": "Complete the test phase",
                "status": "ACHIEVED",
                "stopping_condition": "Readiness verifier passes",
            },
            "implementation_commit": implementation_commit,
            "allowed_evidence_paths_after_implementation_commit": ["harness/"],
            "expected_milestone_ids": ["M0"],
            "milestones": [{"id": "M0", "status": "PASS", "evidence": [evidence]}],
            "expected_acceptance_ids": ["P99-01"],
            "acceptance_criteria": [
                {"id": "P99-01", "status": "PASS", "evidence": [evidence]}
            ],
            "commands": [
                {
                    "id": "final-verification",
                    "command": "test command",
                    "ran": True,
                    "exit_code": 0,
                    "tested_commit": implementation_commit,
                    "evidence": [evidence],
                }
            ],
            "required_checks": [
                {"id": check_id, "status": "PASS", "evidence": [evidence]}
                for check_id in (
                    "final_verification",
                    "generated_artifact_freshness",
                    "source_preservation",
                    "file_boundary",
                    "rendered_workflow",
                    "regression",
                )
            ],
            "reports": {
                "phase_work_record": evidence,
                "execution_log": evidence,
                "verification_summary": evidence,
                "completion_report": evidence,
                "rendered_evidence": evidence,
            },
            "blockers": [],
            "gate": {
                "implementation": "IMPLEMENTATION_COMPLETE_AWAITING_QA",
                "independent_qa": "PENDING",
                "master": "PENDING",
                "phase_seal": "ABSENT",
            },
        }
        manifest_path = root / "harness" / "verify" / "phase-99-readiness.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        run("git", "add", ".", cwd=root)
        run("git", "commit", "-q", "-m", "evidence", cwd=root)
        return manifest_path

    def test_ready_manifest_passes_and_dirty_worktree_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.create_ready_repo(root)
            verifier = root / "harness" / "verify" / SCRIPT.name

            passing = run(
                sys.executable,
                str(verifier),
                "--manifest",
                str(manifest_path),
                cwd=root,
            )
            self.assertIn("IMPLEMENTATION READINESS: PASS", passing.stdout)

            (root / "untracked.tmp").write_text("dirty\n", encoding="utf-8")
            failing = run(
                sys.executable,
                str(verifier),
                "--manifest",
                str(manifest_path),
                cwd=root,
                check=False,
            )
            self.assertEqual(failing.returncode, 1)
            self.assertIn("worktree must be clean", failing.stderr)


if __name__ == "__main__":
    unittest.main()
