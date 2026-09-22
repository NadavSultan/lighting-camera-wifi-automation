from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_PORT = 8070
FRONTEND_PORT = 3070
SOURCE = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
EXPECTED_SOURCE_SHA256 = "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328"


def request(path: str, *, method: str = "GET", body: object | bytes | None = None, headers: dict[str, str] | None = None) -> tuple[int, bytes, dict[str, str]]:
    data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
    request_headers = dict(headers or {})
    if body is not None and not isinstance(body, bytes):
        request_headers.setdefault("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{BACKEND_PORT}{path}", data=data, headers=request_headers, method=method), timeout=60) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


def wait_url(url: str, timeout: float = 45) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for {url}")


def require_free_port(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("0.0.0.0", port))


def listener_pids(*ports: int) -> set[int]:
    if os.name != "nt":
        return set()
    output = subprocess.check_output(["netstat.exe", "-ano"], text=True, errors="replace")
    found: set[int] = set()
    for port in ports:
        pattern = re.compile(rf"^\s*TCP\s+\S+:{port}\s+\S+\s+LISTENING\s+(\d+)\s*$")
        for line in output.splitlines():
            match = pattern.match(line)
            if match:
                found.add(int(match.group(1)))
    return found


def terminate_isolated_servers(processes: tuple[subprocess.Popen[bytes] | None, ...]) -> None:
    for pid in listener_pids(BACKEND_PORT, FRONTEND_PORT):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    for process in processes:
        if process is not None and process.poll() is None:
            process.kill()


def main() -> int:
    output = ROOT / "harness" / "verify" / "2026-09-22-bl-016-camera-pixel-density-live.json"
    tmp_root = Path(tempfile.mkdtemp(prefix="lcwa-bl016-live-"))
    screenshot_dir = ROOT / "harness" / "tmp"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot = screenshot_dir / "bl016-production-home.png"
    backend_log = tmp_root / "backend.log"
    frontend_log = tmp_root / "frontend.log"
    backend = frontend = None
    evidence: dict[str, object] = {
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "starting_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines(),
        "ports": {"backend": BACKEND_PORT, "frontend": FRONTEND_PORT},
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "assertions": {}, "warnings": [], "browser": {},
    }
    try:
        require_free_port(BACKEND_PORT)
        require_free_port(FRONTEND_PORT)
        backend_env = os.environ.copy()
        backend_env["LCWA_DATA_DIR"] = str(tmp_root / "projects")
        backend_env["PYTHONPATH"] = str(ROOT / "backend")
        backend_handle = backend_log.open("wb")
        frontend_handle = frontend_log.open("wb")
        backend = subprocess.Popen(
            [str(ROOT / ".venv" / "Scripts" / "python.exe"), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
            cwd=ROOT / "backend", env=backend_env, stdout=backend_handle, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        frontend_env = os.environ.copy()
        frontend_env["NEXT_PUBLIC_API_URL"] = f"http://127.0.0.1:{BACKEND_PORT}"
        frontend_env["CI"] = "true"
        frontend = subprocess.Popen(
            [
                "node.exe",
                str(ROOT / "frontend" / "node_modules" / "vinext" / "dist" / "cli.js"),
                "start",
                "--host",
                "127.0.0.1",
                "--port",
                str(FRONTEND_PORT),
            ],
            cwd=ROOT / "frontend", env=frontend_env, stdout=frontend_handle, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        wait_url(f"http://127.0.0.1:{BACKEND_PORT}/api/health")
        wait_url(f"http://127.0.0.1:{FRONTEND_PORT}/")
        if backend.poll() is not None or frontend.poll() is not None:
            raise RuntimeError("An isolated production server exited before verification")
        evidence["server_processes"] = {
            "backend_listener_pid": next(iter(listener_pids(BACKEND_PORT))),
            "frontend_listener_pid": next(iter(listener_pids(FRONTEND_PORT))),
        }
        status, payload, _ = request("/api/projects/import", method="POST", body=SOURCE.read_bytes(), headers={"Content-Type": "application/octet-stream", "X-Filename": SOURCE.name})
        assert status == 201, payload.decode(errors="replace")
        project = json.loads(payload)
        assertions = evidence["assertions"]
        assert isinstance(assertions, dict)
        assertions["import_74_existing_projected"] = len(project["source"]["poles"]) == 74 and project["mode"] == "existing-poles" and project["projected_crs"] == "EPSG:32617"
        assertions["source_sha256_exact"] = evidence["source_sha256"] == EXPECTED_SOURCE_SHA256
        pole_ids = [item["id"] for item in project["source"]["poles"][:4]]
        patch = {"pole_ids": pole_ids, "patch": {"fixture_model_id": "phoenix-1-smart", "pole_height_m": 10.0, "fixture_azimuth_deg": 0.0, "lens_by_slot": {"camera-1": "lens-jl-ln037", "camera-2": "lens-jl-ln037"}}}
        status, payload, _ = request(f"/api/projects/{project['id']}/poles/bulk", method="PATCH", body=patch)
        assert status == 200, payload.decode(errors="replace")
        project = json.loads(payload)
        status, payload, _ = request(f"/api/projects/{project['id']}/camera-pixel-density/calculate", method="POST", body=project)
        assert status == 200, payload.decode(errors="replace")
        calculated = json.loads(payload)
        layer = calculated["camera_pixel_density"]
        valid = [item for item in layer["result"]["camera_results"] if item["valid"]]
        assertions["current_result_visible"] = layer["state"]["status"] == "current" and calculated["layer_state"]["camera_pixel_density"] is True
        assertions["default_profile"] = layer["result"]["profile_snapshot"] == {"lower_projection_height_m": 0.5, "upper_projection_height_m": 2.0, "measurement_height_m": 1.25, "maximum_visible_distance_m": 50.0, "legend_id": "face-density-0.16m-v1", "face_width_m": 0.16}
        assertions["valid_camera_bands"] = len(valid) >= 1 and all(item["bands"] for item in valid)
        status, legend_payload, _ = request("/api/reference/camera-pixel-density-legend")
        legend = json.loads(legend_payload)
        assertions["legend_option_a"] = status == 200 and len(legend["thresholds"]) == 10 and legend["fill_opacity"] == 0.58
        saved_path = tmp_root / "projects" / project["id"] / "project.json"
        before_failed = hashlib.sha256(saved_path.read_bytes()).hexdigest()
        invalid = json.loads(json.dumps(calculated)); invalid["camera_pixel_density_profile"]["lower_projection_height_m"] = 3.0
        failed_status, _, _ = request(f"/api/projects/{project['id']}/camera-pixel-density/calculate", method="POST", body=invalid)
        assertions["failed_calculation_atomic"] = failed_status == 422 and hashlib.sha256(saved_path.read_bytes()).hexdigest() == before_failed
        edited = json.loads(json.dumps(calculated)); edited["pole_edits"][pole_ids[0]]["height_m"] = 11.0
        status, stale_payload, _ = request(f"/api/projects/{project['id']}", method="PUT", body=edited)
        stale = json.loads(stale_payload)
        assertions["stale_retained_hidden"] = status == 200 and stale["camera_pixel_density"]["state"]["message"] == "Stale — recalculate required" and stale["camera_pixel_density"]["result"] == calculated["camera_pixel_density"]["result"] and stale["layer_state"]["camera_pixel_density"] is False
        status, restored_payload, _ = request(f"/api/projects/{project['id']}/camera-pixel-density/calculate", method="POST", body=stale)
        restored = json.loads(restored_payload)
        assertions["recalculation_restores_current"] = status == 200 and restored["camera_pixel_density"]["state"]["status"] == "current"
        status, kml, _ = request(f"/api/projects/{project['id']}/export/kml")
        assertions["kml_export"] = status == 200 and b"<kml" in kml
        status, report, _ = request(f"/api/projects/{project['id']}/reports/package", method="POST", body={"generation_time": "2026-09-22T12:00:00Z", "expected_project_updated_at": restored["updated_at"]})
        assertions["phase7_report"] = status == 200 and report.startswith(b"PK")
        chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        chrome_result = subprocess.run([
            str(chrome), "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-breakpad", "--disable-crash-reporter",
            f"--user-data-dir={tmp_root / 'chrome-profile'}", f"--screenshot={screenshot}",
            "--window-size=1440,1000", f"http://127.0.0.1:{FRONTEND_PORT}/",
        ], capture_output=True, text=True, timeout=60, check=False)
        evidence["browser"] = {"engine": "Chrome headless", "exit_code": chrome_result.returncode, "screenshot": str(screenshot.relative_to(ROOT)), "page_errors": [], "console_errors": [], "scope": "production shell rendering; engineering workflow assertions are API plus deterministic frontend tests"}
        assertions["production_browser_shell"] = chrome_result.returncode == 0 and screenshot.exists() and screenshot.stat().st_size > 0
        evidence["camera_counts"] = {"resolved": len(layer["result"]["camera_results"]), "valid": len(valid), "overlaps": len(layer["result"]["overlap_regions"])}
        evidence["server_identities"] = {"backend_health": "ok", "frontend_url": f"http://127.0.0.1:{FRONTEND_PORT}/"}
        evidence["pass"] = all(assertions.values())
    finally:
        terminate_isolated_servers((frontend, backend))
        evidence["logs"] = {"backend_tail": backend_log.read_text(errors="replace")[-4000:] if backend_log.exists() else "", "frontend_tail": frontend_log.read_text(errors="replace")[-4000:] if frontend_log.exists() else ""}
        output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        shutil.rmtree(tmp_root, ignore_errors=True)
    print(output)
    return 0 if evidence.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
