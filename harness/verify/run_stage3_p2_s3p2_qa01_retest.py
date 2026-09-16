"""Focused independent retest of S3P2-QA-01. Does not overwrite original QA JSON."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
KML = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
EXPECTED_SHA = "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328"
OUT = ROOT / "harness" / "verify" / "2026-09-16-stage3-p2-s3p2-qa-01-retest.json"
SHOTS = ROOT / "harness" / "tmp" / "stage3-p2-qa01-retest" / "screenshots"
API_PORT = 8063
UI_PORT = 3063
API = f"http://127.0.0.1:{API_PORT}"
UI = f"http://127.0.0.1:{UI_PORT}/"


def stop_proc(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    if os.name == "nt" and proc.pid:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, check=False)
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except Exception:  # noqa: BLE001
        proc.kill()


def wait_http(url: str, timeout: float = 90.0) -> None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=2.0)
            if response.status_code < 500:
                return
            last = f"HTTP {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            last = exc
        time.sleep(0.4)
    raise RuntimeError(f"timeout waiting for {url}: {last}")


PROBE = """() => {
  const field = document.getElementById('cap-field-product_mapping');
  const details = field ? field.closest('details') : null;
  const required = [...document.querySelectorAll('#cap-planning-panel details.cap-required-inputs')].find((item) => {
    const summary = item.querySelector('summary');
    return summary && summary.textContent.trim() === 'Required CAP inputs';
  });
  const active = document.activeElement;
  return {
    requiredOpen: required ? required.open : null,
    requiredSummary: required?.querySelector('summary')?.textContent?.trim() || null,
    productMappingDetailsOpen: details ? details.open : null,
    productMappingDetailsIsRequired: !!(details && required && details === required),
    activeId: active && active.id,
    activeTag: active && active.tagName,
    fieldVisible: !!(field && field.offsetParent !== null),
    fieldDisabled: field ? field.disabled : null,
  };
}"""


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    kml_bytes = KML.read_bytes()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    record: dict = {
        "identity": "independent-qa-s3p2-qa-01-retest",
        "head": head,
        "kml_sha256": hashlib.sha256(kml_bytes).hexdigest(),
        "expected_sha256": EXPECTED_SHA,
        "api": API,
        "ui": UI,
        "errors": [],
        "does_not_overwrite": str(ROOT / "harness" / "verify" / "2026-09-16-stage3-p2-usability-independent-qa-review.md"),
    }
    data_dir = Path(tempfile.mkdtemp(prefix="lcwa-s3p2-qa01-"))
    record["data_dir"] = str(data_dir)
    env = os.environ.copy()
    env["LCWA_DATA_DIR"] = str(data_dir)
    api_proc = None
    ui_proc = None
    try:
        api_proc = subprocess.Popen(
            [str(ROOT / ".venv" / "Scripts" / "python.exe"), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(API_PORT)],
            cwd=str(ROOT / "backend"),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        ui_env = os.environ.copy()
        ui_env["NEXT_PUBLIC_API_URL"] = API
        ui_proc = subprocess.Popen(
            ["corepack", "pnpm", "exec", "vinext", "start", "--host", "127.0.0.1", "--port", str(UI_PORT)],
            cwd=str(ROOT / "frontend"),
            env=ui_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        wait_http(f"{API}/api/health")
        wait_http(UI)
        record["live_health"] = httpx.get(f"{API}/api/health", timeout=5.0).json()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            )
            page = browser.new_page(viewport={"width": 1920, "height": 855})
            page.on("pageerror", lambda exc: record["errors"].append(f"pageerror:{exc}"))
            page.goto(UI, wait_until="load", timeout=60000)
            page.locator(".discipline-switcher").wait_for(timeout=30000)
            page.set_input_files("input[accept='.kml,.kmz']", str(KML))
            page.locator(".count-card strong").filter(has_text="74").first.wait_for(timeout=60000)
            projects = httpx.get(f"{API}/api/projects", timeout=10.0).json()
            imported = httpx.get(f"{API}/api/projects/{projects[0]['id']}", timeout=30.0).json() if projects else {}
            record["import_sha256"] = ((imported.get("source") or {}).get("file") or {}).get("sha256")
            record["pole_count"] = len((imported.get("source") or {}).get("poles") or [])
            record["mode"] = imported.get("mode")

            page.get_by_role("tab", name="CAP").click()
            page.locator("#cap-planning-panel").wait_for(timeout=10000)
            page.wait_for_timeout(400)
            record["before"] = page.evaluate(PROBE)
            page.screenshot(path=str(SHOTS / "01-before-review.png"))
            review = page.locator("#cap-planning-panel .cap-blocker-list li").filter(has_text="Product mapping").get_by_role("button", name="Review input")
            record["review_button_count"] = review.count()
            review.first.click()
            try:
                page.wait_for_function(
                    """() => {
                      const field = document.getElementById('cap-field-product_mapping');
                      const details = field && field.closest('details');
                      return !!(details && details.open === true && document.activeElement && document.activeElement.id === 'cap-field-product_mapping');
                    }""",
                    timeout=5000,
                )
            except Exception as exc:  # noqa: BLE001
                record["focus_wait_error"] = str(exc)
            page.wait_for_timeout(250)
            record["after"] = page.evaluate(PROBE)
            page.screenshot(path=str(SHOTS / "02-after-review.png"))
            browser.close()

        after = record.get("after") or {}
        before = record.get("before") or {}
        record["hash_ok"] = record["kml_sha256"] == EXPECTED_SHA and record.get("import_sha256") == EXPECTED_SHA
        record["started_collapsed"] = before.get("requiredOpen") is False and before.get("productMappingDetailsOpen") is False
        record["opened_required_details"] = after.get("requiredOpen") is True and after.get("productMappingDetailsIsRequired") is True
        record["focused_product_mapping"] = after.get("activeId") == "cap-field-product_mapping"
        record["field_visible"] = after.get("fieldVisible") is True
        record["no_page_errors"] = not any(str(item).startswith("pageerror:") for item in record["errors"])
        record["s3p2_qa_01"] = all(
            record[key] is True
            for key in ("hash_ok", "started_collapsed", "opened_required_details", "focused_product_mapping", "field_visible", "no_page_errors")
        )
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        summary = {k: record.get(k) for k in (
            "hash_ok", "started_collapsed", "opened_required_details", "focused_product_mapping",
            "field_visible", "no_page_errors", "s3p2_qa_01",
        )}
        print(json.dumps(summary, indent=2))
        print("AFTER", json.dumps(after, indent=2))
        return 0 if record["s3p2_qa_01"] else 1
    except Exception as exc:  # noqa: BLE001
        record["errors"].append(str(exc))
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(str(exc).encode("ascii", "replace").decode("ascii"))
        return 1
    finally:
        stop_proc(ui_proc)
        stop_proc(api_proc)


if __name__ == "__main__":
    raise SystemExit(main())
