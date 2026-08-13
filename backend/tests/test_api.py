from __future__ import annotations

import base64
import copy
import hashlib
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.store import ProjectStore


def test_import_save_reopen_and_export(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "projects")
    client = TestClient(create_app(store))
    source = Path(__file__).resolve().parents[2] / "Input" / "Miracle_Mile_Lighting_Poles.kml"

    imported = client.post(
        "/api/projects/import",
        content=source.read_bytes(),
        headers={"X-Filename": source.name, "Content-Type": "application/octet-stream"},
    )
    assert imported.status_code == 201, imported.text
    project = imported.json()
    assert len(project["source"]["poles"]) == 74
    assert project["mode"] == "existing-poles"

    pole_id = project["source"]["poles"][0]["id"]
    project["pole_edits"][pole_id] = {
        "pole_id": pole_id,
        "fixture_type": "WIFI",
        "height_m": 9.0,
        "engineering_notes": "API round trip",
        "location_edit_authorized": False,
    }
    saved = client.put(f"/api/projects/{project['id']}", json=project)
    assert saved.status_code == 200, saved.text

    reopened = client.get(f"/api/projects/{project['id']}")
    assert reopened.status_code == 200
    assert reopened.json()["pole_edits"][pole_id]["fixture_type"] == "WIFI"

    exported = client.get(f"/api/projects/{project['id']}/export/kml")
    assert exported.status_code == 200
    assert b"lcwa_fixture_type" in exported.content
    assert b"WIFI" in exported.content

    original = tmp_path / "projects" / project["id"] / "sources" / source.name
    assert original.read_bytes() == source.read_bytes()


def test_project_json_open_round_trip(tmp_path: Path) -> None:
    client = TestClient(create_app(ProjectStore(tmp_path / "projects")))
    created = client.post("/api/projects", json={"name": "Local project"})
    assert created.status_code == 201

    opened = client.post("/api/projects/open", json=created.json())
    assert opened.status_code == 200
    assert opened.json()["name"] == "Local project"


def test_rejects_unsupported_upload(tmp_path: Path) -> None:
    client = TestClient(create_app(ProjectStore(tmp_path / "projects")))
    response = client.post(
        "/api/projects/import",
        content=b"not kml",
        headers={"X-Filename": "poles.csv", "Content-Type": "application/octet-stream"},
    )
    assert response.status_code == 422
    assert "Only .kml and .kmz" in response.json()["detail"]


def test_open_rejects_tampered_source_content_and_preserves_saved_project(tmp_path: Path) -> None:
    store_root = tmp_path / "projects"
    client = TestClient(create_app(ProjectStore(store_root)))
    source = Path(__file__).resolve().parents[2] / "Input" / "Miracle_Mile_Lighting_Poles.kml"
    imported = client.post(
        "/api/projects/import",
        content=source.read_bytes(),
        headers={"X-Filename": source.name, "Content-Type": "application/octet-stream"},
    )
    assert imported.status_code == 201
    original_project = imported.json()
    project_path = store_root / original_project["id"] / "project.json"
    saved_bytes = project_path.read_bytes()

    tampered = dict(original_project)
    tampered["source"] = dict(original_project["source"])
    tampered_file = dict(original_project["source"]["file"])
    tampered_bytes = b"<kml>tampered</kml>"
    tampered_file["content_base64"] = base64.b64encode(tampered_bytes).decode("ascii")
    tampered_file["sha256"] = hashlib.sha256(tampered_bytes).hexdigest()
    tampered_file["size_bytes"] = len(tampered_bytes)
    tampered["source"]["file"] = tampered_file

    opened = client.post("/api/projects/open", json=tampered)
    assert opened.status_code == 422
    assert project_path.read_bytes() == saved_bytes
    assert (store_root / original_project["id"] / "sources" / source.name).read_bytes() == source.read_bytes()


def test_open_rejects_source_integrity_mismatch_and_unsafe_filename(tmp_path: Path) -> None:
    client = TestClient(create_app(ProjectStore(tmp_path / "projects")))
    source = Path(__file__).resolve().parents[2] / "Input" / "Miracle_Mile_Lighting_Poles.kml"
    imported = client.post(
        "/api/projects/import",
        content=source.read_bytes(),
        headers={"X-Filename": source.name, "Content-Type": "application/octet-stream"},
    ).json()

    mismatched = dict(imported)
    mismatched["source"] = dict(imported["source"])
    mismatched_file = dict(imported["source"]["file"])
    mismatched_file["sha256"] = "0" * 64
    mismatched["source"]["file"] = mismatched_file
    response = client.post("/api/projects/open", json=mismatched)
    assert response.status_code == 422

    unsafe = dict(imported)
    unsafe["id"] = "unsafe-name-case"
    unsafe["source"] = dict(imported["source"])
    unsafe_file = dict(imported["source"]["file"])
    unsafe_file["filename"] = "../project.json"
    unsafe["source"]["file"] = unsafe_file
    response = client.post("/api/projects/open", json=unsafe)
    assert response.status_code == 422
    assert not (tmp_path / "projects" / "unsafe-name-case" / "project.json").exists()


def test_open_rejects_source_records_that_do_not_match_embedded_kml(tmp_path: Path) -> None:
    client = TestClient(create_app(ProjectStore(tmp_path / "projects")))
    source = Path(__file__).resolve().parents[2] / "Input" / "Miracle_Mile_Lighting_Poles.kml"
    imported = client.post(
        "/api/projects/import",
        content=source.read_bytes(),
        headers={"X-Filename": source.name, "Content-Type": "application/octet-stream"},
    ).json()
    tampered = copy.deepcopy(imported)
    tampered["id"] = "new-portable-project-id"
    tampered["source"]["poles"][0]["longitude"] += 0.001

    response = client.post("/api/projects/open", json=tampered)

    assert response.status_code == 422
    assert "do not match the embedded" in response.json()["detail"]
    assert not (tmp_path / "projects" / "new-portable-project-id").exists()
