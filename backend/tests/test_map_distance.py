import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pyproj import Transformer

from app.main import create_app
from app.services.catalogs import CatalogStore
from app.services.store import ProjectStore

ROOT = Path(__file__).resolve().parents[2]


def body():
    inverse = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    return {"projected_crs": "EPSG:32617",
            "start_wgs84": inverse.transform(580000, 2850000),
            "end_wgs84": inverse.transform(580030, 2850040)}


def client_at(tmp_path):
    return TestClient(create_app(ProjectStore(tmp_path / "projects"),
                                 CatalogStore(tmp_path / "catalogs", ROOT / "data/phase2")))


def test_known_projected_distance_and_zero(tmp_path):
    with client_at(tmp_path) as client:
        payload = body()
        response = client.post("/api/map/distance", json=payload)
        assert response.status_code == 200, response.text
        assert response.json()["distance_m"] == pytest.approx(50, abs=1e-6)
        assert response.json()["projected_crs"] == "EPSG:32617"
        payload["end_wgs84"] = payload["start_wgs84"]
        assert client.post("/api/map/distance", json=payload).json()["distance_m"] == 0


@pytest.mark.parametrize("patch", [
    {"projected_crs": ""}, {"projected_crs": "EPSG:4326"},
    {"projected_crs": "EPSG:2263"}, {"projected_crs": "no-such-crs"},
    {"start_wgs84": [181, 25]}, {"end_wgs84": [-80, 91]},
    {"start_wgs84": [None, 25]}, {"start_wgs84": [1, 2, 3]},
    {"extra": "reject"}, {"projected_crs": None},
])
def test_invalid_coordinate_or_crs(tmp_path, patch):
    with client_at(tmp_path) as client:
        response = client.post("/api/map/distance", json={**body(), **patch})
        assert response.status_code == 422
        assert response.json()["detail"]


def test_distance_api_does_not_persist(tmp_path):
    with client_at(tmp_path) as client:
        created = client.post("/api/projects", json={"name": "untouched"}).json()
        before = {str(p): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
        assert client.post("/api/map/distance", json=body()).status_code == 200
        assert client.post("/api/map/distance", json={**body(), "projected_crs": ""}).status_code == 422
        assert {str(p): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
        stored = tmp_path / "projects" / created["id"] / "project.json"
        assert json.loads(stored.read_bytes()) == created


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_coordinate_is_rejected(tmp_path, value):
    with client_at(tmp_path) as client:
        response = client.post("/api/map/distance", json={**body(), "start_wgs84": [value, 25]})
        assert response.status_code == 422


def test_transform_failures_are_readable(tmp_path, monkeypatch):
    from app.services import map_distance
    from pyproj.exceptions import ProjError
    class BrokenTransformer:
        def transform(self, *args, **kwargs):
            raise ProjError("test transform failure")
    monkeypatch.setattr(map_distance, "project_transformers", lambda crs: (BrokenTransformer(), None))
    with client_at(tmp_path) as client:
        response = client.post("/api/map/distance", json=body())
        assert response.status_code == 422
        assert "transform" in response.json()["detail"]


def test_nonfinite_transform_is_rejected(tmp_path, monkeypatch):
    from app.services import map_distance
    class NonfiniteTransformer:
        def transform(self, *args, **kwargs):
            return float("inf"), 0
    monkeypatch.setattr(map_distance, "project_transformers", lambda crs: (NonfiniteTransformer(), None))
    with client_at(tmp_path) as client:
        response = client.post("/api/map/distance", json=body())
        assert response.status_code == 422
        assert "non-finite" in response.json()["detail"]
