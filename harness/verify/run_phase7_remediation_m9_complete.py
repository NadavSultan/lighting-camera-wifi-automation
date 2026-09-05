"""Remediation M9: API validation + Playwright browser download. Writes verify JSON."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
import tempfile
import zipfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
from reportlab.pdfbase.pdfutils import asciiBase85Decode

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import create_app
from app.models import PresentationModel
from app.services.kml import export_updated_kml
from app.services.store import ProjectStore

INPUT_KML = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
OUT_DIR = ROOT / "harness" / "tmp" / "m9"
SUMMARY = ROOT / "harness" / "verify" / "2026-09-05-phase-7-remediation-m9-summary.json"
FRONTEND = "http://127.0.0.1:13000/"
FIXED_TIME = "2026-09-05T17:00:00Z"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_pdf(pdf: bytes) -> bytes:
    chunks: list[bytes] = []
    idx = 0
    while True:
        start = pdf.find(b"stream", idx)
        if start < 0:
            break
        end = pdf.find(b"endstream", start)
        raw = pdf[start + 6 : end]
        if raw.startswith(b"\r\n"):
            raw = raw[2:]
        elif raw.startswith(b"\n"):
            raw = raw[1:]
        if raw.endswith(b"\r"):
            raw = raw[:-1]
        data = raw if raw.endswith(b"~>") else raw + b"~>"
        try:
            chunks.append(zlib.decompress(asciiBase85Decode(data)))
        except Exception:
            try:
                chunks.append(zlib.decompress(raw))
            except Exception:
                chunks.append(raw)
        idx = end + 9
    return b"\n".join(chunks)


def inspect_xlsx(data: bytes) -> dict:
    forbidden = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        for name in names:
            lower = name.lower()
            if "vbaproject" in lower:
                forbidden.append(name)
            if name.endswith(".rels"):
                text = zf.read(name).decode("utf-8", errors="replace")
                if 'TargetMode="External"' in text or "hyperlink" in text.lower():
                    forbidden.append(f"active-rel:{name}")
    return {"ok": not forbidden, "forbidden_hits": forbidden, "member_count": len(names)}


def run_api() -> dict:
    errors: list[str] = []
    checks: list[dict] = []
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lcwa-m9-") as tmp:
        store = ProjectStore(Path(tmp) / "projects")
        client = TestClient(create_app(store))
        health = client.get("/api/health").json()
        checks.append({"id": "health", "ok": True, "body": health})
        imported = client.post(
            "/api/projects/import",
            content=INPUT_KML.read_bytes(),
            headers={
                "Content-Type": "application/octet-stream",
                "X-Filename": INPUT_KML.name,
                "X-Project-Name": "Miracle Mile M9 Remediation",
            },
        )
        project = imported.json()
        project_id = project["id"]
        poles = len(project["source"]["poles"])
        source_sha = project["source"]["file"]["sha256"]
        checks.append({"id": "import", "ok": poles == 74, "poles": poles, "source_sha256": source_sha})
        if poles != 74:
            errors.append("pole count")
        project = client.get(f"/api/projects/{project_id}").json()
        preview = client.post(f"/api/projects/{project_id}/reports/preview", json={})
        checks.append({"id": "preview", "ok": preview.status_code == 200 and preview.json().get("can_generate")})
        resp = client.post(
            f"/api/projects/{project_id}/reports/package",
            json={
                "generation_time": FIXED_TIME,
                "persist_last_report_metadata": True,
                "expected_project_updated_at": project["updated_at"],
            },
        )
        package = resp.content
        digest = sha256(package)
        (OUT_DIR / "api-package.zip").write_bytes(package)
        header_sha = resp.headers.get("X-Report-Package-SHA256")
        checks.append(
            {
                "id": "package_download",
                "ok": resp.status_code == 200 and header_sha == digest,
                "package_bytes": len(package),
                "package_sha256": digest,
                "header_sha256": header_sha,
                "status": resp.headers.get("X-Report-Status"),
            }
        )
        members = {}
        with zipfile.ZipFile(io.BytesIO(package)) as zf:
            paths = zf.namelist()
            if len(paths) != len(set(paths)):
                errors.append("duplicate paths")
            for name in paths:
                if ".." in name or name.startswith("/"):
                    errors.append(f"unsafe {name}")
                data = zf.read(name)
                members[name] = {"size": len(data), "sha256": sha256(data)}
            manifest = json.loads(zf.read("report-manifest.json").decode())
            if "report-manifest.json" in manifest.get("members", {}):
                errors.append("manifest self-entry")
            for path, meta in manifest["members"].items():
                if members[path]["sha256"] != meta["sha256"] or members[path]["size"] != meta["size_bytes"]:
                    errors.append(f"hash mismatch {path}")
            csv_stats = {
                n: {
                    "row_count": len(list(csv.reader(io.StringIO(zf.read(n).decode())))),
                }
                for n in paths
                if n.startswith("schedules/") and n.endswith(".csv")
            }
            checks.append({"id": "csv_parse", "ok": len(csv_stats) >= 9, "files": csv_stats})
            xlsx_info = inspect_xlsx(zf.read("workbook.xlsx"))
            checks.append({"id": "xlsx_active_content", **xlsx_info})
            kmz_name = next(n for n in paths if n.endswith(".kmz"))
            with zipfile.ZipFile(io.BytesIO(zf.read(kmz_name))) as kmz:
                kml = kmz.read("doc.kml").decode()
            checks.append({"id": "kmz_labels", "ok": "DERIVED" in kml, "kmz_member": kmz_name})
            pdf = zf.read("summary.pdf")
            content = decode_pdf(pdf)
            checks.append(
                {
                    "id": "pdf_vector",
                    "ok": b"Projected overview" in content and b"longitude) Tj" not in content,
                    "page_count": len(re.findall(rb"/Type\s*/Page\b", pdf)),
                    "pdf_bytes": len(pdf),
                }
            )
            presentation = json.loads(zf.read("presentation-model.json").decode())
            PresentationModel.model_validate(presentation)
            try:
                PresentationModel.model_validate({**presentation, "x": 1})
                extra_ok = False
            except Exception:
                extra_ok = True
            checks.append(
                {
                    "id": "presentation_strict",
                    "ok": presentation["presentation_generated"] is False and extra_ok,
                    "inventory_poles": presentation["inventory"]["pole_count"],
                }
            )
            checks.append(
                {
                    "id": "cross_format",
                    "ok": presentation["report_input_sha256"] == manifest["report_input_sha256"],
                    "manifest_status": manifest["status"],
                }
            )
        updated = export_updated_kml(store.load(project_id)).decode()
        checks.append(
            {
                "id": "updated_kml",
                "ok": updated.count("<Placemark") == 74 and "DERIVED" not in updated,
                "placemarks": updated.count("<Placemark"),
            }
        )
    return {
        "health": health,
        "project_id": project_id,
        "poles": poles,
        "source_sha256": source_sha,
        "package_bytes": len(package),
        "package_sha256": digest,
        "package_response_sha256_header": header_sha,
        "manifest_status": manifest["status"],
        "member_count": len(members),
        "members": members,
        "checks": checks,
        "errors": errors,
        "ok": not errors and all(c.get("ok", True) for c in checks),
    }


def run_browser() -> dict:
    console: list[dict] = []
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda msg: console.append({"type": msg.type, "text": msg.text}))
        page.on("pageerror", lambda exc: console.append({"type": "pageerror", "text": str(exc)}))
        page.goto(FRONTEND, wait_until="networkidle", timeout=180_000)
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(str(INPUT_KML))
        page.wait_for_timeout(8000)
        # Wait for poles / project name
        page.get_by_text("Report package", exact=False).first.wait_for(timeout=120_000)
        refresh = page.get_by_role("button", name="Refresh report checklist")
        if refresh.count():
            refresh.first.click()
            page.wait_for_timeout(4000)
        # Toggle a format checkbox if present (PDF)
        pdf_box = page.get_by_text("PDF summary", exact=False)
        if pdf_box.count():
            # click associated checkbox via nearby input
            pass
        generate = page.get_by_role("button", name="Generate / Download report package")
        generate.first.wait_for(state="visible", timeout=120_000)
        # Wait until enabled
        for _ in range(60):
            if generate.first.is_enabled():
                break
            page.wait_for_timeout(1000)
        if not generate.first.is_enabled():
            body = page.inner_text("body")
            browser.close()
            return {"ok": False, "error": "generate disabled", "body_snip": body[:1000], "console": console}
        with page.expect_download(timeout=180_000) as info:
            generate.first.click()
        download = info.value
        target = OUT_DIR / "browser-download.zip"
        download.save_as(str(target))
        data = target.read_bytes()
        errors = [c for c in console if c["type"] in {"error", "pageerror"}]
        browser.close()
        return {
            "ok": len(errors) == 0 and data[:2] == b"PK",
            "frontend": FRONTEND,
            "download_path": str(target.relative_to(ROOT)).replace("\\", "/"),
            "download_sha256": sha256(data),
            "download_bytes": len(data),
            "console_error_count": len(errors),
            "console": console,
            "suggested_filename": download.suggested_filename,
        }


def main() -> int:
    api = run_api()
    browser = run_browser()
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "implementation_commit": "e24b6a16add314393574257a08e539a27673a505",
        **{k: api[k] for k in api if k != "checks"},
        "pdf_page_count": next((c.get("page_count") for c in api["checks"] if c["id"] == "pdf_vector"), None),
        "checks": api["checks"],
        "browser_workflow": browser,
        "ok": api["ok"] and browser.get("ok") is True,
        "artifacts_dir": "harness/tmp/m9",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": summary["ok"], "api_sha": api.get("package_sha256"), "browser_sha": browser.get("download_sha256"), "console_errors": browser.get("console_error_count"), "api_errors": api.get("errors"), "browser_error": browser.get("error")}, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
