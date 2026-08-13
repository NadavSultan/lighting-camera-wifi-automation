from pathlib import Path
import subprocess
import sys


def test_engineering_catalogs_and_sources_validate() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(repository_root / "scripts" / "validate_engineering_data.py")],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
