"""Stage 1 P1 live checks: source hash, direction preview, viewport fit, overlay canvases."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
KML = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
EXPECTED_SHA = "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328"
DATA = ROOT / "harness" / "tmp" / "stage1-p1-data"
OUT = ROOT / "harness" / "tmp" / "stage1-p1-live.json"
API = "http://127.0.0.1:8000"
UI = "http://127.0.0.1:3000/"
VIEWPORTS = [(1920, 855), (1440, 855), (1366, 768), (1024, 768)]


def wait_http(url: str, timeout: float = 60.0) -> None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            httpx.get(url, timeout=2.0)
            return
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(0.4)
    raise RuntimeError(f"timeout waiting for {url}: {last}")


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    kml_bytes = KML.read_bytes()
    kml_sha = hashlib.sha256(kml_bytes).hexdigest()
    record: dict = {"kml_sha256": kml_sha, "expected_sha256": EXPECTED_SHA, "viewports": [], "preview": None, "errors": []}
    sys.path.insert(0, str(ROOT / "backend"))
    os.environ["LCWA_DATA_DIR"] = str(DATA)
    from app.main import create_app  # noqa: E402
    from fastapi.testclient import TestClient  # noqa: E402

    client = TestClient(create_app())
    imported = client.post(
        "/api/projects/import",
        content=kml_bytes,
        headers={"X-Filename": KML.name, "X-Project-Name": "Stage1 P1 client"},
    )
    imported.raise_for_status()
    project = imported.json()
    archive_sha = project["source"]["file"]["sha256"]
    record["source_archive_sha256"] = archive_sha
    record["pole_count"] = len(project["source"]["poles"])
    configured = client.patch(
        f"/api/projects/{project['id']}/poles/bulk",
        json={
            "pole_ids": [project["source"]["poles"][0]["id"]],
            "patch": {"fixture_model_id": "phoenix-1-smart", "fixture_azimuth_deg": 0, "pole_height_m": 8},
        },
    )
    configured.raise_for_status()
    project = configured.json()
    preview = client.post("/api/fixture-directions/preview", json=project)
    preview.raise_for_status()
    body = preview.json()
    record["preview"] = {
        "direction_count": len(body.get("directions") or []),
        "unavailable_count": len(body.get("unavailable") or []),
    }

    env = os.environ.copy()
    env["LCWA_DATA_DIR"] = str(DATA)
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT / "backend"),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    frontend = subprocess.Popen(
        ["corepack", "pnpm", "run", "start"],
        cwd=str(ROOT / "frontend"),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    try:
        wait_http(f"{API}/api/health")
        wait_http(UI)
        record["live_health"] = httpx.get(f"{API}/api/health", timeout=5.0).json()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 855})
            page.goto(UI, wait_until="networkidle")
            page.set_input_files("input[accept='.kml,.kmz']", str(KML))
            page.locator(".count-card strong").filter(has_text="74").first.wait_for(timeout=60000)
            page.locator("#bulk-model option[value='phoenix-1-smart']").wait_for(state="attached", timeout=30000)
            page.locator("#bulk-model").scroll_into_view_if_needed()
            page.locator("#bulk-model").select_option("phoenix-1-smart")
            page.locator("#bulk-azimuth").scroll_into_view_if_needed()
            page.locator("#bulk-azimuth").fill("0")
            page.get_by_role("button", name="Apply selected fields").scroll_into_view_if_needed()
            page.get_by_role("button", name="Apply selected fields").click()
            page.wait_for_timeout(4000)
            record["arrow_pixels_1920"] = page.evaluate(
                """() => {
                  const canvas = document.querySelector('canvas.fixture-direction-arrows');
                  if (!canvas || !canvas.width) return { painted: false, sample: 0 };
                  const ctx = canvas.getContext('2d');
                  const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                  let painted = 0;
                  for (let i = 3; i < data.length; i += 4) {
                    if (data[i] > 8) painted += 1;
                  }
                  return { painted: painted > 0, sample: painted, width: canvas.width, height: canvas.height };
                }"""
            )
            for width, height in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": height})
                page.wait_for_timeout(400)
                metrics = page.evaluate(
                    """() => {
                      const workspace = document.querySelector('.workspace');
                      const inspector = document.querySelector('.side-panel.inspector');
                      const shell = document.querySelector('.app-shell');
                      const canvas = document.querySelector('canvas.fixture-direction-arrows');
                      const labels = document.querySelector('canvas.lighting-point-labels');
                      const probe = document.createElement('aside');
                      probe.className = 'map-overlay lighting-result-card';
                      probe.style.visibility = 'hidden';
                      document.body.appendChild(probe);
                      const card = getComputedStyle(probe);
                      const maxHeight = card.maxHeight;
                      probe.remove();
                      const wr = workspace ? workspace.getBoundingClientRect() : null;
                      const ir = inspector ? inspector.getBoundingClientRect() : null;
                      const sr = shell ? shell.getBoundingClientRect() : null;
                      return {
                        innerWidth: window.innerWidth,
                        workspaceWidth: wr && wr.width,
                        workspaceRight: wr && wr.right,
                        inspectorRight: ir && ir.right,
                        shellWidth: sr && sr.width,
                        overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
                        arrowCanvas: canvas ? { width: canvas.width, height: canvas.height, clientWidth: canvas.clientWidth } : null,
                        labelCanvas: labels ? { width: labels.width, height: labels.height, clientWidth: labels.clientWidth } : null,
                        cardMaxHeight: maxHeight,
                      };
                    }"""
                )
                record["viewports"].append({"width": width, "height": height, **metrics})
            page.evaluate("() => window.dispatchEvent(new Event('resize'))")
            page.wait_for_timeout(800)
            pixels = page.evaluate(
                """() => {
                  const canvas = document.querySelector('canvas.fixture-direction-arrows');
                  if (!canvas || !canvas.width) return { painted: false, sample: 0 };
                  const ctx = canvas.getContext('2d');
                  const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                  let painted = 0;
                  for (let i = 3; i < data.length; i += 16) {
                    if (data[i] > 8) painted += 1;
                  }
                  return { painted: painted > 0, sample: painted, width: canvas.width, height: canvas.height };
                }"""
            )
            record["arrow_pixels"] = record.get("arrow_pixels_1920") or pixels
            browser.close()
        record["hash_ok"] = kml_sha == EXPECTED_SHA and archive_sha == EXPECTED_SHA
        record["layout_ok"] = all(
            (item.get("workspaceRight") or 0) <= item["innerWidth"] + 1
            and (item.get("inspectorRight") or 0) <= item["innerWidth"] + 1
            and not item.get("overflowX")
            for item in record["viewports"]
        )
        record["card_ok"] = all("220px" not in str(item.get("cardMaxHeight") or "") for item in record["viewports"])
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(json.dumps(record, indent=2))
        if not record["hash_ok"] or not record["layout_ok"] or not record["card_ok"]:
            return 1
        return 0
    except Exception as exc:  # noqa: BLE001
        record["errors"].append(str(exc))
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(json.dumps(record, indent=2))
        raise
    finally:
        backend.terminate()
        frontend.terminate()
        try:
            backend.wait(timeout=8)
        except subprocess.TimeoutExpired:
            backend.kill()
        try:
            frontend.wait(timeout=8)
        except subprocess.TimeoutExpired:
            frontend.kill()


if __name__ == "__main__":
    raise SystemExit(main())
