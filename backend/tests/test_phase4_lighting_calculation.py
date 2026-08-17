from __future__ import annotations

import copy
import math
from pathlib import Path

import pytest
from pyproj import Transformer
from shapely.geometry import Polygon

from app.catalog_models import IesFixtureAssociation, IesLibrary
from app.models import CalculationArea, FixtureType, PoleEdit, PoleFixtureConfiguration, Project, SourceLayer, SourcePole, migrate_project_payload
from app.services.catalogs import AUTHORIZED_SUPPLIED_IES_COMPATIBILITY, CatalogStore
from app.services.ies import parse_ies_upload
from app.services.lighting_calculation import (
    MAX_CALCULATION_POINTS,
    EligibleFixture,
    calculate_lighting_area,
    deterministic_grid,
    horizontal_illuminance_lux,
    interpolate_candela,
    parse_type_c_photometry,
)

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


def test_grid_boundary_order_limit_and_exact_recalculation() -> None:
    polygon = Polygon([(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)])
    assert deterministic_grid(polygon, 2) == [(0, 0), (2, 0), (4, 0), (0, 2), (2, 2), (4, 2), (0, 4), (2, 4), (4, 4)]
    too_large = Polygon([(0, 0), (MAX_CALCULATION_POINTS + 1, 0), (MAX_CALCULATION_POINTS + 1, 1), (0, 1), (0, 0)])
    with pytest.raises(ValueError, match="point limit|too many"):
        deterministic_grid(too_large, 1)
    assert deterministic_grid(Polygon([(0.1, 0.1), (0.2, 0.1), (0.2, 0.2), (0.1, 0.2)]), 2) == []


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
    assert migrated["schema_version"] == "2.4.0"
    assert migrated["calculation_areas"] == [] and migrated["lighting_calculations"] == {}
    assert migrated["source"] == payload["source"] and migrated["priority_areas"] == payload["priority_areas"]
