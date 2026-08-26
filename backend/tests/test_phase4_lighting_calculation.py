from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pyproj import Transformer
from shapely.geometry import Polygon

from app.catalog_models import IesFixtureAssociation, IesLibrary
from app.main import create_app
from app.models import CalculationArea, FixtureType, LightingCalculationPoint, LightingStatistics, MIN_GRID_SPACING_M, PoleEdit, PoleFixtureConfiguration, Project, SourceLayer, SourcePole, migrate_project_payload
from app.services.catalogs import AUTHORIZED_SUPPLIED_IES_COMPATIBILITY, CatalogStore
from app.services.ies import IesValidationError, parse_ies_upload, resolve_pinned_ies_revision
from app.services.lighting_calculation import (
    MAX_CALCULATION_POINTS,
    EligibleFixture,
    calculate_lighting_area,
    deterministic_grid,
    horizontal_illuminance_lux,
    invalidate_stale_lighting_results,
    interpolate_candela,
    lighting_calculation_input_sha256,
    parse_type_c_photometry,
)
from app.services.store import ProjectStore

ROOT = Path(__file__).resolve().parents[2]


def synthetic_ies(rows: list[list[float]], vertical: list[float] | None = None, horizontal: list[float] | None = None, multiplier: float = 1.0, luminaire: str = "SYNTHETIC") -> bytes:
    vertical = vertical or [0.0, 45.0, 90.0]
    horizontal = horizontal or [0.0, 90.0, 180.0, 270.0, 360.0]
    assert len(rows) == len(horizontal) and all(len(row) == len(vertical) for row in rows)
    header = f"1 -1 {multiplier} {len(vertical)} {len(horizontal)} 1 2 0 0 0 1 0 50"
    values = " ".join(str(value) for row in rows for value in row)
    return (f"IESNA:LM-63-2002\n[MANUFAC] TEST\n[LUMINAIRE] {luminaire}\nTILT=NONE\n{header}\n{' '.join(map(str, vertical))}\n{' '.join(map(str, horizontal))}\n{values}\n").encode()


def constant_record(intensity: float = 1000.0):
    return parse_ies_upload("constant.ies", synthetic_ies([[intensity] * 3 for _ in range(5)]))


def project_at_lattice(record, maintenance_factor: float = 1.0, spacing: float = 2.0) -> tuple[Project, CalculationArea]:
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    longitude, latitude = to_wgs84.transform(600_000.0, 2_850_000.0)
    ring = [to_wgs84.transform(x, y) for x, y in ((599_997.9, 2_849_997.9), (600_002.1, 2_849_997.9), (600_002.1, 2_850_002.1), (599_997.9, 2_850_002.1), (599_997.9, 2_849_997.9))]
    pole = SourcePole(id="pole-1", sequence_index=0, name="Pole 1", longitude=longitude, latitude=latitude, raw_coordinates=f"{longitude},{latitude},0")
    area = CalculationArea(id="area-1", name="Road", classification="ROAD", wgs84_coordinates=ring, grid_spacing_m=spacing, maintenance_factor=maintenance_factor)
    project = Project(projected_crs="EPSG:32617", source=SourceLayer(poles=[pole]), calculation_areas=[area])
    project.pole_edits[pole.id] = PoleEdit(
        pole_id=pole.id, fixture_type=FixtureType.LITE, height_m=10,
        fixture_configuration=PoleFixtureConfiguration(
            fixture_model_id="phoenix-1-lite", fixture_model_revision=1, ies_file_id=record.id,
            ies_file_revision=record.revision, fixture_azimuth_deg=0,
        ),
    )
    return project, area


def catalogs_and_library(record):
    fixture_catalog = CatalogStore(root=ROOT / "backend" / "data" / "does-not-exist").fixtures()
    library = IesLibrary(files=[record], fixture_associations=[IesFixtureAssociation(ies_file_id=record.id, fixture_model_id="phoenix-1-lite")])
    return fixture_catalog, library


def calculated_api_project(tmp_path: Path):
    revision_1 = constant_record(1000)
    revision_1.id = "ies-input-r1"
    revision_2 = parse_ies_upload("second.ies", synthetic_ies([[2000.0] * 3 for _ in range(5)]))
    revision_2.id = "ies-input-r2"
    catalog_store = CatalogStore(root=tmp_path / "catalogs", seed_root=ROOT / "data" / "phase2")
    catalog_store.save_ies(IesLibrary(
        files=[revision_1, revision_2],
        fixture_associations=[
            IesFixtureAssociation(ies_file_id=revision_1.id, fixture_model_id="phoenix-1-lite"),
            IesFixtureAssociation(ies_file_id=revision_1.id, fixture_model_id="solitaire-lite"),
            IesFixtureAssociation(ies_file_id=revision_2.id, fixture_model_id="phoenix-1-lite"),
        ],
    ))
    project, area = project_at_lattice(revision_1)
    project_store = ProjectStore(tmp_path / "projects")
    project_store.save(project)
    client = TestClient(create_app(project_store, catalog_store))
    calculated = client.post(
        f"/api/projects/{project.id}/lighting/calculate/{area.id}", json=project.model_dump(mode="json")
    )
    assert calculated.status_code == 200, calculated.text
    assert calculated.json()["lighting_calculations"]["results"][area.id]["calculation_input_sha256"]
    return client, project_store, catalog_store, calculated.json(), area.id, revision_1, revision_2


def test_constant_intensity_nadir_off_axis_inverse_square_and_incidence() -> None:
    record = constant_record()
    photometry = parse_type_c_photometry(record)
    provenance = None
    fixture = EligibleFixture("pole", 0, 0, 10, 0, photometry, provenance)  # type: ignore[arg-type]
    assert horizontal_illuminance_lux(fixture, 0, 0, 0) == pytest.approx(10.0)
    expected = 1000 * 10 / (104 ** 1.5)
    assert horizontal_illuminance_lux(fixture, 2, 0, 0) == pytest.approx(expected)
    assert horizontal_illuminance_lux(fixture, 4, 0, 0) < horizontal_illuminance_lux(fixture, 2, 0, 0)


def test_vertical_c_plane_and_seam_interpolation_are_deterministic() -> None:
    record = parse_ies_upload("asymmetric.ies", synthetic_ies([[0, 100, 200], [1000, 1100, 1200], [2000, 2100, 2200], [3000, 3100, 3200], [0, 100, 200]]))
    photometry = parse_type_c_photometry(record)
    assert interpolate_candela(photometry, 22.5, 45) == pytest.approx(550)
    assert interpolate_candela(photometry, 22.5, 359) == pytest.approx(83.3333333333)
    assert interpolate_candela(photometry, 22.5, 0) == pytest.approx(50)
    assert interpolate_candela(photometry, 22.5, 360) == pytest.approx(50)


@pytest.mark.parametrize(("horizontal", "rows"), [
    ([37.0], [[100.0, 100.0, 100.0]]),
    ([0.0, 90.0], [[100.0, 100.0, 100.0], [200.0, 200.0, 200.0]]),
    ([0.0, 180.0], [[100.0, 100.0, 100.0], [200.0, 200.0, 200.0]]),
    ([0.0, 180.0, 360.0], [[100.0, 100.0, 100.0], [200.0, 200.0, 200.0], [100.0, 100.0, 100.0]]),
])
def test_approved_type_c_horizontal_domains_are_accepted(horizontal: list[float], rows: list[list[float]]) -> None:
    record = parse_ies_upload("domain.ies", synthetic_ies(rows, horizontal=horizontal))
    assert record.validation_status == "valid"
    assert parse_type_c_photometry(record).horizontal_angles_deg == tuple(horizontal)


def test_unsupported_partial_c_domain_and_discontinuous_full_seam_are_rejected() -> None:
    with pytest.raises(IesValidationError, match="Unsupported Type C horizontal domain"):
        parse_ies_upload("partial.ies", synthetic_ies([[100.0] * 3, [200.0] * 3], horizontal=[10.0, 20.0]))
    with pytest.raises(IesValidationError, match="0/360 C-plane seam is discontinuous"):
        parse_ies_upload(
            "seam.ies",
            synthetic_ies([[100.0] * 3, [200.0] * 3, [900.0] * 3], horizontal=[0.0, 180.0, 360.0]),
        )


def test_grid_boundary_order_limit_and_exact_recalculation() -> None:
    polygon = Polygon([(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)])
    assert deterministic_grid(polygon, 2) == [(0, 0), (2, 0), (4, 0), (0, 2), (2, 2), (4, 2), (0, 4), (2, 4), (4, 4)]
    too_large = Polygon([(0, 0), (MAX_CALCULATION_POINTS + 1, 0), (MAX_CALCULATION_POINTS + 1, 1), (0, 1), (0, 0)])
    with pytest.raises(ValueError, match="point limit|too many"):
        deterministic_grid(too_large, 1)
    assert deterministic_grid(Polygon([(0.1, 0.1), (0.2, 0.1), (0.2, 0.2), (0.1, 0.2)]), 2) == []


def test_boundary_tolerance_expands_minimum_maximum_edge_and_vertex_candidates() -> None:
    inside = 9.99e-8
    outside = 1.001e-7
    assert (0, 0) in deterministic_grid(Polygon([(inside, -1), (1, -1), (1, 1), (inside, 1)]), 1)
    assert (1, 0) in deterministic_grid(Polygon([(-1, -1), (1 - inside, -1), (1 - inside, 1), (-1, 1)]), 1)
    assert (0, 0) in deterministic_grid(Polygon([(-1, inside), (1, inside), (1, 1), (-1, 1)]), 1)
    assert (0, 1) in deterministic_grid(Polygon([(-1, -1), (1, -1), (1, 1 - inside), (-1, 1 - inside)]), 1)
    vertex_offset = inside / math.sqrt(2)
    vertex_points = deterministic_grid(Polygon([
        (vertex_offset, vertex_offset), (1, vertex_offset), (1, 1), (vertex_offset, 1)
    ]), 1)
    assert (0, 0) in vertex_points
    assert len(vertex_points) == len(set(vertex_points))
    rejected = deterministic_grid(Polygon([(outside, -1), (1, -1), (1, 1), (outside, 1)]), 1)
    assert (0, 0) not in rejected
    outside_vertex_offset = outside / math.sqrt(2)
    rejected_vertex = deterministic_grid(Polygon([
        (outside_vertex_offset, outside_vertex_offset), (1, outside_vertex_offset), (1, 1), (outside_vertex_offset, 1)
    ]), 1)
    assert (0, 0) not in rejected_vertex


def test_non_finite_models_and_overflow_photometry_are_rejected() -> None:
    with pytest.raises(IesValidationError, match="non-finite scaled intensity"):
        parse_ies_upload(
            "overflow.ies",
            synthetic_ies([[1e308] * 3 for _ in range(5)], multiplier=1e308),
        )
    with pytest.raises(ValidationError):
        LightingCalculationPoint(
            id="bad", sequence_index=0, projected_coordinate_m=(0, 0), wgs84_coordinate=(0, 0),
            calculation_plane_elevation_m=0, maintained_horizontal_illuminance_lux=math.inf,
        )
    with pytest.raises(ValidationError):
        LightingStatistics(point_count=1, grid_spacing_m=2, average_illuminance_lux=math.nan)


def test_invalid_crs_and_unsafe_spacing_return_controlled_errors_and_preserve_project(tmp_path: Path) -> None:
    client, projects, _, calculated, area_id, _, _ = calculated_api_project(tmp_path)
    prior_result = copy.deepcopy(calculated["lighting_calculations"]["results"][area_id])
    for invalid_crs in ("NOT-A-CRS", "EPSG:4326", "EPSG:2263"):
        projects.save(Project.model_validate(copy.deepcopy(calculated)))
        payload = copy.deepcopy(calculated)
        payload["projected_crs"] = invalid_crs
        response = client.post(f"/api/projects/{calculated['id']}/lighting/calculate/{area_id}", json=payload)
        assert response.status_code == 422, (invalid_crs, response.text)
        assert "CRS" in str(response.json()["detail"])
        reopened = client.get(f"/api/projects/{calculated['id']}")
        assert reopened.status_code == 200
        assert reopened.json()["lighting_calculations"]["results"][area_id] == prior_result

    subnormal = copy.deepcopy(calculated)
    subnormal["calculation_areas"][0]["grid_spacing_m"] = 5e-324
    response = client.post(f"/api/projects/{calculated['id']}/lighting/calculate/{area_id}", json=subnormal)
    assert response.status_code == 422
    assert "greater than or equal to 0.01" in response.text

    lower_boundary = copy.deepcopy(calculated)
    lower_boundary["calculation_areas"][0]["grid_spacing_m"] = MIN_GRID_SPACING_M
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    lower_boundary["calculation_areas"][0]["wgs84_coordinates"] = [
        to_wgs84.transform(x, y)
        for x, y in ((599999.989, 2849999.989), (600000.011, 2849999.989), (600000.011, 2850000.011), (599999.989, 2850000.011), (599999.989, 2849999.989))
    ]
    accepted = client.post(f"/api/projects/{calculated['id']}/lighting/calculate/{area_id}", json=lower_boundary)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["lighting_calculations"]["results"][area_id]["statistics"]["grid_spacing_m"] == MIN_GRID_SPACING_M


def test_corrupt_non_finite_persisted_project_returns_422_not_not_found(tmp_path: Path) -> None:
    client, projects, _, calculated, area_id, _, _ = calculated_api_project(tmp_path)
    corrupted = copy.deepcopy(calculated)
    corrupted["lighting_calculations"]["results"][area_id]["points"][0]["maintained_horizontal_illuminance_lux"] = math.inf
    project_path = projects.root / calculated["id"] / "project.json"
    project_path.write_text(json.dumps(corrupted), encoding="utf-8")
    response = client.get(f"/api/projects/{calculated['id']}")
    assert response.status_code == 422
    assert "invalid or corrupt" in response.json()["detail"]


def test_area_calculation_statistics_maintenance_sum_and_provenance() -> None:
    record = constant_record()
    project, area = project_at_lattice(record, maintenance_factor=0.8)
    fixtures, library = catalogs_and_library(record)
    result = calculate_lighting_area(project, area.id, fixtures, library)
    assert result.statistics.point_count == 9
    center = result.points[4]
    assert center.projected_coordinate_m == (600_000.0, 2_850_000.0)
    assert center.maintained_horizontal_illuminance_lux == pytest.approx(8.0)
    assert result.statistics.average_illuminance_lux == pytest.approx(sum(point.maintained_horizontal_illuminance_lux for point in result.points) / 9)
    assert result.statistics.emin_over_eavg is not None and result.statistics.emin_over_emax is not None
    assert result.fixture_provenance[0].origin_projected_m[:2] == pytest.approx((600_000, 2_850_000), abs=1e-6)
    assert result.disclaimer.startswith("Not independently validated")
    repeated = calculate_lighting_area(copy.deepcopy(project), area.id, fixtures, library)
    assert [(p.id, p.projected_coordinate_m, p.maintained_horizontal_illuminance_lux) for p in repeated.points] == [(p.id, p.projected_coordinate_m, p.maintained_horizontal_illuminance_lux) for p in result.points]


def test_calculation_significant_save_restore_and_bulk_mutations_invalidate_results(tmp_path: Path) -> None:
    client, projects, _, calculated, area_id, _, revision_2 = calculated_api_project(tmp_path)

    note_only = copy.deepcopy(calculated)
    note_only["pole_edits"]["pole-1"]["engineering_notes"] = "No photometric change"
    note_saved = client.put(f"/api/projects/{calculated['id']}", json=note_only)
    assert note_saved.status_code == 200, note_saved.text
    assert area_id in note_saved.json()["lighting_calculations"]["results"]

    for change in ("height", "azimuth", "model", "ies", "active", "restore"):
        projects.save(Project.model_validate(copy.deepcopy(calculated)))
        payload = copy.deepcopy(calculated)
        edit = payload["pole_edits"]["pole-1"]
        config = edit["fixture_configuration"]
        if change == "height":
            edit["height_m"] = 20
        elif change == "azimuth":
            config["fixture_azimuth_deg"] = 90
        elif change == "model":
            config["fixture_model_id"] = "solitaire-lite"
            config["fixture_model_revision"] = 1
        elif change == "ies":
            config["ies_file_id"] = revision_2.id
            config["ies_file_revision"] = revision_2.revision
        elif change == "active":
            edit["active"] = False
        else:
            del payload["pole_edits"]["pole-1"]
        saved = client.put(f"/api/projects/{calculated['id']}", json=payload)
        assert saved.status_code == 200, f"{change}: {saved.text}"
        assert saved.json()["lighting_calculations"]["results"] == {}, change
        assert saved.json()["calculation_areas"][0]["calculation_state"]["status"] == "not-calculated"
        reopened = client.get(f"/api/projects/{calculated['id']}")
        assert reopened.status_code == 200
        assert reopened.json()["lighting_calculations"]["results"] == {}, change

    projects.save(Project.model_validate(copy.deepcopy(calculated)))
    bulk = client.patch(
        f"/api/projects/{calculated['id']}/poles/bulk",
        json={"pole_ids": ["pole-1"], "patch": {"pole_height_m": 15, "fixture_azimuth_deg": 45}},
    )
    assert bulk.status_code == 200, bulk.text
    assert bulk.json()["lighting_calculations"]["results"] == {}


def test_input_signature_invalidates_old_or_mismatched_results_without_touching_notes() -> None:
    record = constant_record()
    project, area = project_at_lattice(record)
    fixtures, library = catalogs_and_library(record)
    result = calculate_lighting_area(project, area.id, fixtures, library)
    project.lighting_calculations.results[area.id] = result
    expected = lighting_calculation_input_sha256(project, area.id)
    assert result.calculation_input_sha256 == expected
    project.pole_edits["pole-1"].engineering_notes = "note only"
    assert invalidate_stale_lighting_results(project) is False
    project.pole_edits["pole-1"].height_m = 11
    assert invalidate_stale_lighting_results(project) is True
    assert project.lighting_calculations.results == {}


def test_historical_ies_pin_survives_revision_update_until_explicit_reselection(tmp_path: Path) -> None:
    revision_1 = parse_ies_upload("revision-1.ies", synthetic_ies([[1000.0] * 3 for _ in range(5)]))
    revision_1.id = "ies-immutable-history-test"
    revision_1.validation_warnings = ["preserved revision-1 warning"]
    fixtures = CatalogStore(root=tmp_path / "catalogs", seed_root=ROOT / "data" / "phase2")
    fixtures.save_ies(IesLibrary(
        files=[revision_1],
        fixture_associations=[IesFixtureAssociation(ies_file_id=revision_1.id, fixture_model_id="phoenix-1-lite")],
    ))
    project, area = project_at_lattice(revision_1)
    projects = ProjectStore(tmp_path / "projects")
    projects.save(project)
    client = TestClient(create_app(projects, fixtures))

    initial = client.post(f"/api/projects/{project.id}/lighting/calculate/{area.id}", json=project.model_dump(mode="json"))
    assert initial.status_code == 200, initial.text
    revision_1_project = initial.json()
    revision_1_result = revision_1_project["lighting_calculations"]["results"][area.id]
    revision_1_center = revision_1_result["points"][4]["maintained_horizontal_illuminance_lux"]
    assert revision_1_center == pytest.approx(10.0)

    revision_2 = parse_ies_upload("revision-2.ies", synthetic_ies([[2000.0] * 3 for _ in range(5)]))
    revision_2.id = revision_1.id
    revision_2.revision = 2
    revision_2.validation_warnings = ["revision-2 warning"]
    advanced = IesLibrary(
        files=[revision_2], file_history=[revision_1],
        fixture_associations=[IesFixtureAssociation(ies_file_id=revision_1.id, fixture_model_id="phoenix-1-lite")],
    )
    fixtures.save_ies(advanced)
    reopened_library = fixtures.ies()
    assert [(record.id, record.revision, record.sha256) for record in reopened_library.file_history] == [
        (revision_1.id, 1, revision_1.sha256)
    ]

    saved = client.put(f"/api/projects/{project.id}", json=revision_1_project)
    assert saved.status_code == 200, saved.text
    assert saved.json()["pole_edits"]["pole-1"]["fixture_configuration"]["ies_file_revision"] == 1
    historical = client.post(f"/api/projects/{project.id}/lighting/calculate/{area.id}", json=saved.json())
    assert historical.status_code == 200, historical.text
    historical_project = historical.json()
    historical_result = historical_project["lighting_calculations"]["results"][area.id]
    historical_provenance = historical_result["fixture_provenance"][0]
    assert historical_result["points"][4]["maintained_horizontal_illuminance_lux"] == pytest.approx(revision_1_center)
    assert historical_provenance["ies_file_revision"] == 1
    assert historical_provenance["ies_sha256"] == revision_1.sha256
    assert historical_provenance["ies_original_filename"] == "revision-1.ies"
    assert historical_provenance["ies_parsed_metadata"] == revision_1.parsed_metadata.model_dump(mode="json")
    assert historical_provenance["warnings"] == ["preserved revision-1 warning"]
    repeated = client.post(f"/api/projects/{project.id}/lighting/calculate/{area.id}", json=historical_project)
    assert repeated.status_code == 200, repeated.text
    assert repeated.json()["pole_edits"]["pole-1"]["fixture_configuration"]["ies_file_revision"] == 1
    assert repeated.json()["lighting_calculations"]["results"][area.id]["points"] == historical_result["points"]

    adopted = client.patch(
        f"/api/projects/{project.id}/poles/bulk",
        json={"pole_ids": ["pole-1"], "patch": {"ies_file_id": revision_2.id}},
    )
    assert adopted.status_code == 200, adopted.text
    assert adopted.json()["pole_edits"]["pole-1"]["fixture_configuration"]["ies_file_revision"] == 2
    revision_2_calculation = client.post(
        f"/api/projects/{project.id}/lighting/calculate/{area.id}", json=adopted.json()
    )
    assert revision_2_calculation.status_code == 200, revision_2_calculation.text
    revision_2_result = revision_2_calculation.json()["lighting_calculations"]["results"][area.id]
    assert revision_2_result["points"][4]["maintained_horizontal_illuminance_lux"] == pytest.approx(20.0)
    assert revision_2_result["fixture_provenance"][0]["ies_file_revision"] == 2
    assert revision_2_result["fixture_provenance"][0]["ies_sha256"] == revision_2.sha256
    assert revision_2_result["fixture_provenance"][0]["ies_original_filename"] == "revision-2.ies"

    missing_history = IesLibrary(
        files=[revision_2],
        fixture_associations=[IesFixtureAssociation(ies_file_id=revision_2.id, fixture_model_id="phoenix-1-lite")],
    )
    fixtures.save_ies(missing_history)
    stale_payload = revision_2_calculation.json()
    stale_payload["pole_edits"]["pole-1"]["fixture_configuration"]["ies_file_revision"] = 1
    rejected = client.put(f"/api/projects/{project.id}", json=stale_payload)
    assert rejected.status_code == 422
    assert "revision 1 is missing; current revision was not substituted" in rejected.json()["detail"]


@pytest.mark.parametrize("metadata_patch", [
    {"input_watts": 999.0},
    {"vertical_angle_count": 99},
    {"horizontal_angle_range_deg": (10.0, 20.0)},
])
def test_historical_resolver_reparses_bytes_and_rejects_metadata_mismatch(metadata_patch: dict[str, object]) -> None:
    revision_1 = constant_record(1000)
    revision_1.id = "ies-metadata-integrity"
    corrupted_metadata = revision_1.parsed_metadata.model_copy(update=metadata_patch)  # type: ignore[union-attr]
    corrupted = revision_1.model_copy(update={"parsed_metadata": corrupted_metadata})
    revision_2 = constant_record(2000)
    revision_2.id = revision_1.id
    revision_2.revision = 2
    library = IesLibrary(
        files=[revision_2], file_history=[corrupted],
        fixture_associations=[IesFixtureAssociation(ies_file_id=revision_1.id, fixture_model_id="phoenix-1-lite")],
    )
    with pytest.raises(ValueError, match="revision 1 parsed metadata does not match its immutable bytes"):
        resolve_pinned_ies_revision(library, revision_1.id, 1, "phoenix-1-lite")
    assert resolve_pinned_ies_revision(library, revision_1.id, 2, "phoenix-1-lite").pinned_record.sha256 == revision_2.sha256


def test_historical_resolver_accepts_canonical_metadata_and_rejects_missing_metadata() -> None:
    revision_1 = constant_record(1000)
    revision_1.id = "ies-canonical-history"
    revision_2 = constant_record(2000)
    revision_2.id = revision_1.id
    revision_2.revision = 2
    association = IesFixtureAssociation(ies_file_id=revision_1.id, fixture_model_id="phoenix-1-lite")
    valid_library = IesLibrary(files=[revision_2], file_history=[revision_1], fixture_associations=[association])
    resolved = resolve_pinned_ies_revision(valid_library, revision_1.id, 1, "phoenix-1-lite")
    assert resolved.pinned_record.parsed_metadata == revision_1.parsed_metadata

    missing_payload = revision_1.model_dump()
    missing_payload["parsed_metadata"] = None
    missing = type(revision_1).model_construct(**missing_payload)
    unsafe_library = IesLibrary.model_construct(files=[revision_2], file_history=[missing], fixture_associations=[association])
    with pytest.raises(ValueError, match="revision 1 is corrupt"):
        resolve_pinned_ies_revision(unsafe_library, revision_1.id, 1, "phoenix-1-lite")


def test_new_ies_assignment_uses_only_current_active_valid_revision_and_referenced_deactivation_conflicts(tmp_path: Path) -> None:
    catalogs = CatalogStore(root=tmp_path / "catalogs", seed_root=ROOT / "data" / "phase2")
    record = constant_record()
    record.id = "ies-new-assignment-test"
    catalogs.save_ies(IesLibrary(
        files=[record],
        fixture_associations=[IesFixtureAssociation(ies_file_id=record.id, fixture_model_id="phoenix-1-lite")],
    ))
    project, _ = project_at_lattice(record)
    projects = ProjectStore(tmp_path / "projects")
    projects.save(project)
    client = TestClient(create_app(projects, catalogs))
    deactivation = client.patch(f"/api/catalogs/ies/{record.id}", json={"active": False})
    assert deactivation.status_code == 409
    association_deactivation = client.put(
        f"/api/catalogs/ies/{record.id}/fixtures/phoenix-1-lite", json={"active": False}
    )
    assert association_deactivation.status_code == 409
    association_removal = client.delete(f"/api/catalogs/ies/{record.id}/fixtures/phoenix-1-lite")
    assert association_removal.status_code == 409

    inactive = copy.deepcopy(record)
    inactive.active = False
    inactive.revision = 2
    catalogs.save_ies(IesLibrary(files=[inactive], file_history=[record]))
    assignment = client.patch(
        f"/api/projects/{project.id}/poles/bulk",
        json={"pole_ids": ["pole-1"], "patch": {"ies_file_id": record.id}},
    )
    assert assignment.status_code == 422
    assert "inactive, invalid, or unsupported current record" in assignment.json()["detail"]

    invalid = type(inactive).model_validate({
        **inactive.model_dump(),
        "revision": 3,
        "validation_status": "invalid",
        "validation_errors": ["synthetic invalid current revision"],
    })
    catalogs.save_ies(IesLibrary(files=[invalid], file_history=[record, inactive]))
    invalid_assignment = client.patch(
        f"/api/projects/{project.id}/poles/bulk",
        json={"pole_ids": ["pole-1"], "patch": {"ies_file_id": record.id}},
    )
    assert invalid_assignment.status_code == 422
    assert "inactive, invalid, or unsupported current record" in invalid_assignment.json()["detail"]


def test_multiple_fixture_summation_and_rotation_never_moves_origin() -> None:
    rows = [[1000] * 3, [2000] * 3, [3000] * 3, [4000] * 3, [1000] * 3]
    record = parse_ies_upload("asymmetric.ies", synthetic_ies(rows))
    project, area = project_at_lattice(record)
    fixtures, library = catalogs_and_library(record)
    first = calculate_lighting_area(project, area.id, fixtures, library)
    north = next(point for point in first.points if point.projected_coordinate_m == (600_000, 2_850_002))
    origin_before = first.fixture_provenance[0].origin_projected_m
    project.pole_edits["pole-1"].fixture_configuration.fixture_azimuth_deg = 90  # type: ignore[union-attr]
    rotated = calculate_lighting_area(project, area.id, fixtures, library)
    north_rotated = next(point for point in rotated.points if point.projected_coordinate_m == (600_000, 2_850_002))
    assert north_rotated.maintained_horizontal_illuminance_lux == pytest.approx(north.maintained_horizontal_illuminance_lux * 4)
    assert rotated.fixture_provenance[0].origin_projected_m == origin_before
    second_pole = copy.deepcopy(project.source.poles[0]); second_pole.id = "pole-2"; second_pole.sequence_index = 1
    project.source.poles.append(second_pole)
    second_edit = copy.deepcopy(project.pole_edits["pole-1"]); second_edit.pole_id = "pole-2"; project.pole_edits["pole-2"] = second_edit
    summed = calculate_lighting_area(project, area.id, fixtures, library)
    assert summed.contributing_fixture_count == 2
    assert summed.points[4].maintained_horizontal_illuminance_lux == pytest.approx(rotated.points[4].maintained_horizontal_illuminance_lux * 2)


def test_empty_ineligible_and_zero_uniformity_are_explicit() -> None:
    record = constant_record(0)
    project, area = project_at_lattice(record, spacing=100)
    original_ring = copy.deepcopy(area.wgs84_coordinates)
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    area.wgs84_coordinates = [to_wgs84.transform(x, y) for x, y in ((600000.9, 2850000.9), (600001.1, 2850000.9), (600001.1, 2850001.1), (600000.9, 2850001.1), (600000.9, 2850000.9))]
    fixtures, library = catalogs_and_library(record)
    empty = calculate_lighting_area(project, area.id, fixtures, library)
    assert empty.statistics.point_count == 0 and empty.statistics.average_illuminance_lux is None
    assert any("zero calculation points" in warning for warning in empty.warnings)
    area.wgs84_coordinates = original_ring
    area.grid_spacing_m = 2
    zero = calculate_lighting_area(project, area.id, fixtures, library)
    assert zero.statistics.average_illuminance_lux == 0
    assert zero.statistics.emin_over_eavg is None and zero.statistics.emin_over_emax is None
    project.pole_edits["pole-1"].fixture_configuration.ies_file_id = None  # type: ignore[union-attr]
    project.pole_edits["pole-1"].fixture_configuration.ies_file_revision = None  # type: ignore[union-attr]
    excluded = calculate_lighting_area(project, area.id, fixtures, library)
    assert excluded.contributing_fixture_count == 0
    assert any("explicit compatible IES" in warning for warning in excluded.warnings)


def test_all_four_supplied_ies_parse_and_calculate_as_smoke_cases() -> None:
    paths = sorted(path for path in (ROOT / "Input" / "Lighting").iterdir() if path.suffix.lower() == ".ies")
    assert len(paths) == 4
    for path in paths:
        record = parse_ies_upload(path.name, path.read_bytes())
        photometry = parse_type_c_photometry(record)
        assert len(photometry.vertical_angles_deg) == 73 and len(photometry.horizontal_angles_deg) == 145
        assert math.isfinite(interpolate_candela(photometry, 30, 359.5))
        expected_family = "phoenix-1" if "PHOENIX" in path.name.upper() else "solitaire"
        assert AUTHORIZED_SUPPLIED_IES_COMPATIBILITY[record.sha256] == {f"{expected_family}-{variant}" for variant in ("lite", "wifi", "smart")}
    solitaire = [parse_ies_upload(path.name, path.read_bytes()) for path in paths if "SOLITAIRE" in path.name.upper()]
    for record in solitaire:
        project, area = project_at_lattice(record)
        fixtures, library = catalogs_and_library(record)
        library.fixture_associations[0].fixture_model_id = "solitaire-lite"
        project.pole_edits["pole-1"].fixture_configuration.fixture_model_id = "solitaire-lite"  # type: ignore[union-attr]
        result = calculate_lighting_area(project, area.id, fixtures, library)
        assert any("50 W" in warning and "60W" in warning for warning in result.fixture_provenance[0].warnings)
        if any(value < 0 for value in parse_type_c_photometry(record).dimensions_raw):
            assert any("Negative luminous-opening" in warning for warning in result.fixture_provenance[0].warnings)


def test_supplied_ies_cross_family_association_is_rejected_without_a_default() -> None:
    path = ROOT / "Input" / "Lighting" / "JLED-SL-100W-PHOENIX1-40-D01.ies"
    record = parse_ies_upload(path.name, path.read_bytes())
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as directory:
        catalogs = CatalogStore(root=Path(directory), seed_root=ROOT / "data" / "phase2")
        catalogs.add_ies(record)
        with pytest.raises(ValueError, match="explicitly restricted"):
            catalogs.associate_ies(IesFixtureAssociation(ies_file_id=record.id, fixture_model_id="solitaire-lite"))
        catalogs.associate_ies(IesFixtureAssociation(ies_file_id=record.id, fixture_model_id="phoenix-1-lite"))
        assert next(item for item in catalogs.fixtures().fixture_models if item.id == "phoenix-1-lite").default_ies_file_id is None


def test_projected_crs_grid_is_safe_at_high_latitude() -> None:
    to_wgs84 = Transformer.from_crs("EPSG:32631", "EPSG:4326", always_xy=True)
    ring = [to_wgs84.transform(x, y) for x, y in ((499999, 8881999), (500001, 8881999), (500001, 8882001), (499999, 8882001), (499999, 8881999))]
    area = CalculationArea(id="polar", name="High latitude", classification="OTHER", wgs84_coordinates=ring, grid_spacing_m=1)
    projected = Transformer.from_crs("EPSG:4326", "EPSG:32631", always_xy=True)
    polygon = Polygon([projected.transform(*point) for point in area.wgs84_coordinates])
    points = deterministic_grid(polygon, 1)
    assert (500000, 8882000) in points
    assert all(abs(x) > 1000 and abs(y) > 1000 for x, y in points)


@pytest.mark.parametrize("version", ["1.0.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0"])
def test_phase4_additive_migration_preserves_prior_data_and_starts_empty(version: str) -> None:
    record = constant_record()
    project, _ = project_at_lattice(record)
    payload = project.model_dump(mode="json")
    payload["schema_version"] = version
    payload.pop("calculation_areas", None); payload.pop("lighting_calculations", None)
    migrated = migrate_project_payload(payload)
    assert migrated["schema_version"] == "2.5.0"
    assert migrated["calculation_areas"] == [] and migrated["lighting_calculations"] == {}
    assert migrated["source"] == payload["source"] and migrated["priority_areas"] == payload["priority_areas"]
    assert migrated["pole_edits"]["pole-1"]["fixture_configuration"]["ies_file_revision"] == record.revision
