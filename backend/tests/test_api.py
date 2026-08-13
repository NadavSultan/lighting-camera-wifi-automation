from __future__ import annotations

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
