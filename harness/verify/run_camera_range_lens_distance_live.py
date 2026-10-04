"""Ownership-safe isolated servers and API evidence; UI verification uses cua."""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import sys
import subprocess
import time
import urllib.request
import urllib.error
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = Path(os.environ.get("CAMERA_UX_RUNTIME", ROOT / "harness/tmp/camera-ux-runtime-01"))
MANIFEST = RUNTIME / "runtime.json"


def observed_app():
    """Test-only ASGI observer: preserve real request/response coordinates for QA."""
    from app.main import app

    async def wrapper(scope, receive, send):
        if scope.get("type") != "http" or scope.get("method") != "POST" or scope.get("path") != "/api/map/distance":
            return await app(scope, receive, send)
        body, response = bytearray(), bytearray()
        status = None
        def hashes():
            return {str(p.relative_to(RUNTIME)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for directory in ["projects", "catalogs"] for p in (RUNTIME / directory).rglob("*") if p.is_file()}
        before = hashes()
        async def observed_receive():
            message = await receive()
            body.extend(message.get("body", b""))
            return message
        async def observed_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                if fault == "delay-next":
                    await asyncio.sleep(3)
            response.extend(message.get("body", b""))
            await send(message)
        flag = RUNTIME / "distance-fault.txt"
        fault = flag.read_text().strip() if flag.exists() else ""
        if fault == "delay-next":
            flag.write_text("consumed")
        if fault == "fail-next":
            flag.write_text("consumed")
            while True:
                message = await observed_receive()
                if not message.get("more_body"):
                    break
            await observed_send({"type": "http.response.start", "status": 422, "headers": [(b"content-type", b"application/json"), (b"access-control-allow-origin", b"http://127.0.0.1:3070")]})
            await observed_send({"type": "http.response.body", "body": b'{"detail":"Controlled QA distance failure"}'})
        else:
            await app(scope, observed_receive, observed_send)
        event = {"request": json.loads(body), "status": status, "response": json.loads(response),
                 "project_catalog_bytes_unchanged": before == hashes(), "controlled_fault": fault == "fail-next"}
        with (RUNTIME / "browser-distance.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps(event) + "\n")
    return wrapper


def request(path, body=None, method=None, headers=None):
    data = body if isinstance(body, bytes) else json.dumps(body).encode() if body is not None else None
    headers = headers or ({"Content-Type": "application/json"} if data else {})
    req = urllib.request.Request("http://127.0.0.1:8070" + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def serve():
    if MANIFEST.exists():
        raise RuntimeError("Runtime manifest exists; inspect it instead of replacing owned-process records")
    # Check all ports before starting anything; a failed preflight never stops listeners.
    for port in [8070, 3070]:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    RUNTIME.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "LCWA_DATA_DIR": str(RUNTIME / "projects"), "LCWA_CATALOG_DIR": str(RUNTIME / "catalogs"),
           "PYTHONPATH": str(ROOT / "backend"), "CAMERA_UX_RUNTIME": str(RUNTIME), "NEXT_PUBLIC_API_URL": "http://127.0.0.1:8070", "CI": "true"}
    commands = [
        [str(ROOT / ".venv/Scripts/python.exe"), "-m", "uvicorn", "run_camera_range_lens_distance_live:observed_app", "--app-dir", str(ROOT / "harness/verify"), "--factory", "--host", "127.0.0.1", "--port", "8070"],
        ["node.exe", str(ROOT / "frontend/node_modules/vinext/dist/cli.js"), "start", "--host", "127.0.0.1", "--port", "3070"],
    ]
    records = []
    for kind, cmd in zip(["backend", "frontend"], commands):
        with (RUNTIME / f"{kind}.log").open("wb") as log:
            process = subprocess.Popen(cmd, cwd=ROOT / kind, env=env, stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
        records.append({"pid": process.pid, "kind": kind, "command": cmd})
        MANIFEST.write_text(json.dumps({"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                                        "root": str(ROOT), "processes": records}, indent=2))
    for url in ["http://127.0.0.1:8070/api/health", "http://127.0.0.1:3070/"]:
        for attempt in range(120):
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(0.25)
        else:
            raise RuntimeError(f"Server not ready: {url}; owned manifest/logs preserved")
    print(MANIFEST)


def verify():
    source = ROOT / "Input/Miracle_Mile_Lighting_Poles.kml"
    status, raw = request("/api/projects/import", source.read_bytes(), "POST",
                          {"Content-Type": "application/octet-stream", "X-Filename": source.name})
    assert status == 201, raw
    project = json.loads(raw)
    original_source = project["source"]
    assert len(project["source"]["poles"]) == 74
    selected = [p["id"] for p in project["source"]["poles"][:10]]
    status, raw = request(f"/api/projects/{project['id']}/poles/bulk",
                         {"pole_ids": selected, "patch": {"fixture_model_id": "phoenix-1-smart", "pole_height_m": 10,
                          "lens_by_slot": {"camera-1": "lens-jl-ln039", "camera-2": "lens-jl-ln039"}}}, "PATCH")
    assert status == 200, raw
    project = json.loads(raw)
    phase3 = project["camera_geometry"]
    from pyproj import Transformer
    forward = Transformer.from_crs("EPSG:4326", project["projected_crs"], always_xy=True)
    origins = {pole["id"]: forward.transform(pole["longitude"], pole["latitude"]) for pole in project["source"]["poles"]}
    checks = {"import_74": True, "source_hash": hashlib.sha256(source.read_bytes()).hexdigest() == "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328"}
    for maximum in [50, 25, 75]:
        project["camera_pixel_density_profile"]["maximum_visible_distance_m"] = maximum
        status, raw = request(f"/api/projects/{project['id']}/camera-pixel-density/calculate", project, "POST")
        assert status == 200, raw
        project = json.loads(raw)
        checks[f"range_{maximum}_current"] = project["camera_pixel_density"]["state"]["status"] == "current"
        # Existing recalculate paths refresh timestamps; compare stored geometry and metrics.
        checks[f"range_{maximum}_phase3_metrics"] = all(project["camera_geometry"][key] == phase3[key]
            for key in ["footprints", "overlaps", "priority_area_summaries"])
        checks[f"range_{maximum}_bounded"] = all(
            math.hypot(point[0] - origins[camera["pole_id"]][0], point[1] - origins[camera["pole_id"]][1]) <= maximum + 1e-7
            for camera in project["camera_pixel_density"]["result"]["camera_results"] if camera["valid"]
            for polygon in camera["projection_envelope"]["projected_rings_m"] for ring in polygon for point in ring)
    saved_path = RUNTIME / "projects" / project["id"] / "project.json"
    before_failed = saved_path.read_bytes()
    invalid = json.loads(json.dumps(project))
    invalid["camera_pixel_density_profile"]["lower_projection_height_m"] = 3
    status, _ = request(f"/api/projects/{project['id']}/camera-pixel-density/calculate", invalid, "POST")
    checks["failed_calculation_atomic"] = status == 422 and saved_path.read_bytes() == before_failed
    previous_result = project["camera_pixel_density"]["result"]
    project["pole_edits"][selected[0]]["height_m"] = 11
    status, raw = request(f"/api/projects/{project['id']}", project, "PUT")
    project = json.loads(raw)
    checks["stale_retained_hidden"] = status == 200 and project["camera_pixel_density"]["state"]["status"] == "stale" and project["camera_pixel_density"]["result"] == previous_result and not project["layer_state"]["camera_pixel_density"]
    status, raw = request(f"/api/projects/{project['id']}/camera-pixel-density/calculate", project, "POST")
    project = json.loads(raw)
    checks["recalculation_restores_current"] = status == 200 and project["camera_pixel_density"]["state"]["status"] == "current"
    status, raw = request("/api/reference/camera-pixel-density-legend")
    legend = json.loads(raw)
    checks["legend_option_a"] = status == 200 and len(legend["thresholds"]) == 10 and legend["fill_opacity"] == .58
    status, raw = request(f"/api/projects/{project['id']}/export/kml")
    checks["kml_export"] = status == 200 and b"<kml" in raw
    status, raw = request(f"/api/projects/{project['id']}/reports/package", {"generation_time": "2026-10-04T12:00:00Z", "expected_project_updated_at": project["updated_at"]}, "POST")
    checks["phase7_report"] = status == 200 and raw.startswith(b"PK")
    checks["source_poles_unchanged"] = project["source"] == original_source
    from pyproj import Transformer
    inverse = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    start, end = inverse.transform(580000, 2850000), inverse.transform(580030, 2850040)
    before = {str(p): p.read_bytes() for p in (RUNTIME / "projects").rglob("*") if p.is_file()}
    status, raw = request("/api/map/distance", {"projected_crs": "EPSG:32617", "start_wgs84": start, "end_wgs84": end})
    checks["distance_50m"] = status == 200 and abs(json.loads(raw)["distance_m"] - 50) < 1e-6
    checks["distance_no_persistence"] = before == {str(p): p.read_bytes() for p in (RUNTIME / "projects").rglob("*") if p.is_file()}
    project["camera_pixel_density_profile"]["maximum_visible_distance_m"] = 50
    status, raw = request(f"/api/projects/{project['id']}/camera-pixel-density/calculate", project, "POST")
    assert status == 200
    (RUNTIME / "browser-project.json").write_bytes(raw)
    evidence = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "runtime": json.loads(MANIFEST.read_text()), "assertions": checks, "pass": all(checks.values()),
                "scope": "API assertions only; separate cua production-browser evidence required",
                "reference_measurement": {"start_wgs84": start, "end_wgs84": end, "distance_m": 50},
                "browser_project_path": str(RUNTIME / "browser-project.json")}
    (RUNTIME / "api-evidence.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))
    assert evidence["pass"]


def stop():
    data = json.loads(MANIFEST.read_text())
    assert data["root"] == str(ROOT)
    for record in data["processes"]:
        # Verify PID identity against the command's worktree-specific argument before stopping its tree.
        pid = int(record["pid"])
        raw = subprocess.check_output(["powershell", "-NoProfile", "-Command",
            f"$ErrorActionPreference='Stop'; (Get-CimInstance Win32_Process -Filter 'ProcessId={pid}' -ErrorAction Stop).CommandLine"], text=True).strip()
        identity = str(ROOT / "frontend/node_modules/vinext/dist/cli.js") if record["kind"] == "frontend" else str(ROOT / ".venv/Scripts/python.exe")
        if raw and identity.lower() in raw.lower():
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=True)
        elif raw:
            raise RuntimeError(f"PID identity changed: {pid}; refusing to stop it")
    print("Only owned process trees stopped; runtime logs/data retained.")


def analyze(export_path, concurrent_reopen_event=None):
    from pyproj import Transformer
    sys.path.insert(0, str(ROOT / "backend"))
    from app.models import Project
    events = [json.loads(line) for line in (RUNTIME / "browser-distance.jsonl").read_text().splitlines()]
    excluded = [] if concurrent_reopen_event is None else [concurrent_reopen_event]
    assert all(0 <= index < len(events) for index in excluded)
    uncontended = [event for index, event in enumerate(events) if index not in excluded]
    measurements = []
    for event in events:
        if event["status"] != 200:
            continue
        data = event["request"]
        transformer = Transformer.from_crs("EPSG:4326", data["projected_crs"], always_xy=True)
        a, b = transformer.transform(*data["start_wgs84"], errcheck=True), transformer.transform(*data["end_wgs84"], errcheck=True)
        reference = math.hypot(b[0] - a[0], b[1] - a[1])
        measurements.append({**event, "independent_reference_m": reference,
                             "absolute_error_m": abs(event["response"]["distance_m"] - reference)})
    exported = json.loads(export_path.read_text())
    Project.model_validate(exported)
    evidence = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "events": events, "measurements": measurements, "export_sha256": hashlib.sha256(export_path.read_bytes()).hexdigest(),
                "concurrent_reopen_event_indices": excluded,
                "observer_limitation": "Whole request-window hashes include concurrent Open Project writes. Explicitly identified reopen events remain raw evidence but cannot establish endpoint non-persistence; uncontended requests and backend tests do.",
                "assertions": {
                    "all_reference_errors_below_1e_6": all(m["absolute_error_m"] < 1e-6 for m in measurements),
                    "browser_50m_click_tolerance": any(abs(m["independent_reference_m"] - 50) < .1 and m["request"]["start_wgs84"][0] < -80.25 for m in measurements),
                    "all_uncontended_distance_requests_read_only": bool(uncontended) and all(event["project_catalog_bytes_unchanged"] for event in uncontended),
                    "controlled_error_recorded": any(event["controlled_fault"] and event["status"] == 422 for event in events),
                    "export_has_only_project_model_fields": set(exported) == set(Project.model_fields),
                    "export_no_measurement_fields": all(key not in exported for key in ["measurement", "measurementState", "map_distance", "distanceM"]),
                }}
    evidence["pass"] = all(evidence["assertions"].values())
    (RUNTIME / "measurement-evidence.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence["assertions"], indent=2))
    assert evidence["pass"]


def preview(project_id=None):
    from pyproj import Transformer
    from shapely.geometry import Point, Polygon
    from shapely.ops import unary_union
    original = json.loads((RUNTIME / "browser-project.json").read_text())
    identity = str(UUID(project_id)) if project_id else original["id"]
    project = json.loads((RUNTIME / "projects" / identity / "project.json").read_text())
    result = project["camera_pixel_density"]["result"]
    cameras = [camera for camera in result["camera_results"] if camera["valid"]]
    polygons = lambda multi: [Polygon(rings[0], rings[1:]) for rings in multi]
    envelopes = unary_union([polygon for camera in cameras for polygon in polygons(camera["projection_envelope"]["projected_rings_m"])])
    bands = unary_union([polygon for camera in cameras for band in camera["bands"] for polygon in polygons(band["projected_rings_m"])])
    metrics = {key: project["camera_geometry"][key] for key in ["footprints", "overlaps", "priority_area_summaries"]}
    below_threshold_sample = None
    if result["profile_snapshot"]["maximum_visible_distance_m"] >= 280:
        camera = next(camera for camera in cameras if camera["horizontal_fov_deg"] > 80 and camera["camera_slot_id"] == "camera-2")
        pole = next(pole for pole in project["source"]["poles"] if pole["id"] == camera["pole_id"])
        forward = Transformer.from_crs("EPSG:4326", project["projected_crs"], always_xy=True)
        inverse = Transformer.from_crs(project["projected_crs"], "EPSG:4326", always_xy=True)
        x, y = forward.transform(pole["longitude"], pole["latitude"])
        azimuth, tilt = math.radians(camera["camera_absolute_azimuth_deg"]), math.radians(camera["fixed_downward_tilt_deg"])
        point = Point(x + 280 * math.sin(azimuth), y + 280 * math.cos(azimuth))
        height_delta = camera["fixture_height_m"] - result["profile_snapshot"]["measurement_height_m"]
        depth = 280 * math.cos(tilt) + height_delta * math.sin(tilt)
        density = camera["resolution_width_px"] * .16 / (2 * math.tan(math.radians(camera["horizontal_fov_deg"]) / 2) * depth)
        below_threshold_sample = {"camera": camera["footprint_id"], "wgs84": inverse.transform(point.x, point.y),
                                  "radial_distance_m": 280, "forward_depth_m": depth, "independent_px_per_face": density,
                                  "in_preview": envelopes.covers(point), "in_any_density_band": bands.covers(point)}
        print(json.dumps(below_threshold_sample, indent=2))
        assert density < 2 and below_threshold_sample["in_preview"] and not below_threshold_sample["in_any_density_band"]
    evidence = {"verification_version": 2, "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "range_m": result["profile_snapshot"]["maximum_visible_distance_m"], "state": project["camera_pixel_density"]["state"]["status"],
                "preview_without_density_area_m2": envelopes.difference(bands).area,
                "phase3_geometry_metrics_sha256": hashlib.sha256(json.dumps(metrics, sort_keys=True).encode()).hexdigest(),
                "source_poles_unchanged": project["source"]["poles"] == original["source"]["poles"],
                "source_file_bytes_unchanged": all(project["source"]["file"][key] == original["source"]["file"][key]
                                                   for key in ["filename", "sha256", "size_bytes", "content_base64", "source_crs"]),
                "below_threshold_sample": below_threshold_sample}
    with (RUNTIME / "browser-preview.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps(evidence) + "\n")
    print(json.dumps(evidence, indent=2))
    assert evidence["state"] == "current" and evidence["source_poles_unchanged"] and evidence["source_file_bytes_unchanged"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["serve", "verify", "stop", "analyze", "preview"])
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--project")
    parser.add_argument("--concurrent-project-reopen-event", type=int)
    args = parser.parse_args()
    if args.runtime:
        RUNTIME = args.runtime.resolve()
        RUNTIME.relative_to((ROOT / "harness/tmp").resolve())
        MANIFEST = RUNTIME / "runtime.json"
    if args.mode == "analyze":
        analyze(args.export, args.concurrent_project_reopen_event)
    elif args.mode == "preview":
        preview(args.project)
    else:
        {"serve": serve, "verify": verify, "stop": stop}[args.mode]()
