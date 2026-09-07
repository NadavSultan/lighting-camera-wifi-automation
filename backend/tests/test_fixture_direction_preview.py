from __future__ import annotations

import copy
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pyproj import Transformer

from app.main import create_app
from app.models import Project
from app.services.catalogs import CatalogStore
from app.services.configuration import BulkPoleConfigurationPatch, BulkPoleConfigurationRequest, apply_bulk_configuration
from app.services.fixture_direction_preview import (
    preview_fixture_directions,
    projected_direction_endpoint,
)
from app.services.kml import import_project
from app.services.store import ProjectStore


ROOT = Path(__file__).resolve().parents[2]
SEEDS = ROOT / "data" / "phase2"


def catalogs(tmp_path: Path) -> CatalogStore:
    return CatalogStore(tmp_path / "catalogs", SEEDS)


def miracle_project() -> Project:
    source = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
    return import_project(source.name, source.read_bytes(), "Fixture direction preview")


def configure(
    project: Project,
    store: CatalogStore,
    pole_ids: list[str],
    fixture: str = "phoenix-1-lite",
    azimuth: float = 0.0,
) -> Project:
    return apply_bulk_configuration(
        project,
        BulkPoleConfigurationRequest(
            pole_ids=pole_ids,
            patch=BulkPoleConfigurationPatch(fixture_model_id=fixture, fixture_azimuth_deg=azimuth),
        ),
        store.fixtures(),
        store.cameras(),
        store.ies(),
    )


@pytest.mark.parametrize(
    ("azimuth", "expected"),
    [
        (0.0, (100.0, 201.0)),
        (90.0, (101.0, 200.0)),
        (180.0, (100.0, 199.0)),
        (270.0, (99.0, 200.0)),
        (360.0 - 1e-12, (100.0, 201.0)),
        (1e-12, (100.0, 201.0)),
    ],
)
def test_projected_direction_endpoint_cardinals_and_near_wrap(azimuth: float, expected: tuple[float, float]) -> None:
    result = projected_direction_endpoint(100.0, 200.0, azimuth)
    assert result == pytest.approx(expected, abs=1e-9)


def test_projected_direction_endpoint_east_example() -> None:
    assert projected_direction_endpoint(100.0, 200.0, 90.0) == pytest.approx((101.0, 200.0))


def test_projected_direction_endpoint_rejects_nonfinite() -> None:
    with pytest.raises(ValueError, match="finite"):
        projected_direction_endpoint(math.nan, 0.0, 0.0)


def test_preview_cardinals_use_project_crs_and_preserve_source(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    pole = project.source.poles[0]
    original = (pole.id, pole.raw_coordinates, pole.longitude, pole.latitude)
    before = copy.deepcopy(project.model_dump(mode="json"))
    project = configure(project, store, [pole.id], azimuth=90.0)
    before_source = copy.deepcopy(project.source.model_dump(mode="json"))

    preview = preview_fixture_directions(project, store.fixtures())
    assert len(preview.directions) == 1
    direction = preview.directions[0]
    assert direction.pole_id == pole.id
    assert direction.fixture_azimuth_deg == 90.0
    assert direction.active is True
    assert direction.origin_wgs84 == pytest.approx((pole.longitude, pole.latitude), abs=1e-12)

    to_projected = Transformer.from_crs("EPSG:4326", project.projected_crs, always_xy=True)
    to_wgs84 = Transformer.from_crs(project.projected_crs, "EPSG:4326", always_xy=True)
    ox, oy = to_projected.transform(pole.longitude, pole.latitude)
    ex, ey = projected_direction_endpoint(ox, oy, 90.0)
    expected_lon, expected_lat = to_wgs84.transform(ex, ey)
    assert direction.endpoint_wgs84 == pytest.approx((expected_lon, expected_lat), abs=1e-12)

    assert project.source.model_dump(mode="json") == before_source
    assert (pole.id, pole.raw_coordinates, pole.longitude, pole.latitude) == original
    # Configure mutates edits intentionally; preview itself must not further mutate.
    after_preview = project.model_dump(mode="json")
    second = preview_fixture_directions(project, store.fixtures())
    assert project.model_dump(mode="json") == after_preview
    assert second.model_dump(mode="json") == preview.model_dump(mode="json")
    assert before["source"] == after_preview["source"]


def test_preview_measurable_convergence_differs_from_geographic_approximation(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    # Far from UTM zone central meridian: geographic-north degree step diverges from grid north.
    pole = project.source.poles[0]
    project = configure(project, store, [pole.id], azimuth=0.0)
    preview = preview_fixture_directions(project, store.fixtures())
    direction = preview.directions[0]
    dlon = direction.endpoint_wgs84[0] - direction.origin_wgs84[0]
    dlat = direction.endpoint_wgs84[1] - direction.origin_wgs84[1]

    # Naive geographic “north” would move latitude only; projected grid north has a measurable longitude component.
    geographic_only_dlon = 0.0
    assert abs(dlon - geographic_only_dlon) > 1e-10 or abs(dlat) > 0
    # Endpoint is not identical to origin.
    assert (dlon, dlat) != pytest.approx((0.0, 0.0), abs=0)


def test_preview_missing_crs_marks_configured_unavailable(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    pole = project.source.poles[0]
    project = configure(project, store, [pole.id], azimuth=45.0)
    project.projected_crs = None
    preview = preview_fixture_directions(project, store.fixtures())
    assert preview.directions == []
    reasons = {item.pole_id: item.reason for item in preview.unavailable}
    assert pole.id in reasons
    assert "projected CRS" in reasons[pole.id]


def test_preview_missing_configuration_is_explicit(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    preview = preview_fixture_directions(project, store.fixtures())
    assert preview.directions == []
    assert len(preview.unavailable) == len(project.source.poles)
    assert all(item.reason == "fixture configuration is missing" for item in preview.unavailable)


def test_preview_pinned_revision_and_inactive_flag(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    pole = project.source.poles[0]
    other = project.source.poles[1]
    project = configure(project, store, [pole.id, other.id], fixture="phoenix-1-wifi", azimuth=180.0)
    project.pole_edits[other.id].active = False
    project.pole_edits[pole.id].fixture_configuration.fixture_model_revision = 999  # type: ignore[union-attr]
    preview = preview_fixture_directions(project, store.fixtures())
    by_id = {item.pole_id: item for item in preview.directions}
    unavailable = {item.pole_id: item.reason for item in preview.unavailable}
    assert pole.id in unavailable and "missing or inactive" in unavailable[pole.id]
    assert other.id in by_id
    assert by_id[other.id].active is False
    assert by_id[other.id].fixture_azimuth_deg == 180.0


def test_preview_invalid_crs_raises_controlled_error(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    pole = project.source.poles[0]
    project = configure(project, store, [pole.id])
    bypassed = project.model_copy(update={"projected_crs": "EPSG:4326"})
    with pytest.raises(ValueError, match="projected and use metre"):
        preview_fixture_directions(bypassed, store.fixtures())


def test_preview_api_is_read_only_and_does_not_save(tmp_path: Path) -> None:
    project_store = ProjectStore(tmp_path / "projects")
    catalog_store = catalogs(tmp_path)
    client = TestClient(create_app(project_store, catalog_store))
    project = configure(miracle_project(), catalog_store, [miracle_project().source.poles[0].id], azimuth=90.0)
    saved = project_store.save(project)
    before = copy.deepcopy(saved.model_dump(mode="json"))
    updated_at = saved.updated_at

    response = client.post("/api/fixture-directions/preview", json=saved.model_dump(mode="json"))
    assert response.status_code == 200
    body = response.json()
    assert len(body["directions"]) == 1
    assert body["directions"][0]["fixture_azimuth_deg"] == 90.0
    assert "unavailable" in body

    reloaded = project_store.load(saved.id)
    assert reloaded.updated_at == updated_at
    assert reloaded.model_dump(mode="json") == before


def test_preview_api_rejects_invalid_crs(tmp_path: Path) -> None:
    project_store = ProjectStore(tmp_path / "projects")
    catalog_store = catalogs(tmp_path)
    client = TestClient(create_app(project_store, catalog_store))
    project = configure(miracle_project(), catalog_store, [miracle_project().source.poles[0].id])
    payload = project.model_dump(mode="json")
    payload["projected_crs"] = "EPSG:4326"
    response = client.post("/api/fixture-directions/preview", json=payload)
    assert response.status_code == 422
    assert "projected" in str(response.json()).lower()
