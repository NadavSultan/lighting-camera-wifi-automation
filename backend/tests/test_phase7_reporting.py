"""Phase 7 reporting acceptance tests (P7-DM through P7-AT / limits).

Contract: harness/phases/phase-07.md. Implementation: app.services.reporting + SCHEMA 2.7.0 models.
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pyproj import Transformer

from app.main import create_app
from app.models import (
    MAX_REPORT_CELL_CHARS,
    MAX_REPORT_PACKAGE_BYTES,
    SCHEMA_VERSION,
    SOFTWARE_VERSION,
    CalculationArea,
    CapCandidateSite,
    CapConstraintValue,
    CapKnowledge,
    CapNodeDisposition,
    CapPlanningLimits,
    CapPlanningResult,
    FixtureType,
    LastReportMetadata,
    LightingCalculationResult,
    LightingStatistics,
    PoleEdit,
    PriorityArea,
    Project,
    ReportFormatSelection,
    ReportPackageRequest,
    ReportPreferences,
    ReportSectionSelection,
    SourceLayer,
    SourcePole,
    migrate_project_payload,
)
from app.services import reporting
from app.services.cap_planning import apply_cap_result, calculate_cap_plan, cap_input_sha256
from app.services.catalogs import CatalogStore
from app.services.kml import export_updated_kml, import_project
from app.services.lighting_calculation import lighting_calculation_input_sha256
from app.services.reporting import (
    CSV_SPECS,
    ReportGenerationError,
    build_snapshot,
    generate_report_package,
    preview_report,
    safe_cell,
    safe_zip_path,
)
from app.services.store import ProjectStore
from app.services.wifi_coverage import apply_wifi_result, calculate_wifi_coverage, wifi_calculation_input_sha256

ROOT = Path(__file__).resolve().parents[2]
FIXED_TIME = datetime(2026, 9, 4, 12, 0, 0, tzinfo=timezone.utc)

SIMPLE_KML = b"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Test Site</name>
    <Folder><name>Existing Poles</name>
      <Placemark id="customer-1">
        <name>Pole A</name>
        <Point><coordinates>-80.1,25.7,0</coordinates></Point>
      </Placemark>
    </Folder>
  </Document>
</kml>"""


def bare_project(**kwargs):
    return Project(
        source=SourceLayer(
            poles=[
                SourcePole(
                    id="p1",
                    sequence_index=0,
                    name="P1",
                    longitude=-80.1,
                    latitude=25.7,
                    raw_coordinates="-80.1,25.7,0",
                )
            ]
        ),
        projected_crs="EPSG:32617",
        **kwargs,
    )


def fixed_request(**kwargs) -> ReportPackageRequest:
    return ReportPackageRequest(generation_time=FIXED_TIME, **kwargs)


def _zip_members(package: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def _manifest_from_package(package: bytes) -> dict:
    return json.loads(_zip_members(package)["report-manifest.json"].decode("utf-8"))


def _closed_ring_near_pole() -> list[tuple[float, float]]:
    return [(-80.101, 25.699), (-80.099, 25.699), (-80.099, 25.701), (-80.101, 25.701), (-80.101, 25.699)]


def project_with_cap_inputs() -> Project:
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    poles = []
    for i, x in enumerate((600000, 600010)):
        lon, lat = to_wgs84.transform(x, 2850000)
        poles.append(
            SourcePole(
                id=f"p{i}",
                sequence_index=i,
                name=f"P{i}",
                longitude=lon,
                latitude=lat,
                raw_coordinates=f"{lon},{lat},0",
            )
        )
    project = Project(projected_crs="EPSG:32617", source=SourceLayer(poles=poles))
    project.pole_edits["p0"] = PoleEdit(pole_id="p0", fixture_type=FixtureType.WIFI)
    project.pole_edits["p1"] = PoleEdit(pole_id="p1", fixture_type=FixtureType.WIFI)
    known = lambda value, unit=None: CapConstraintValue(
        status=CapKnowledge.KNOWN,
        value=value,
        unit=unit,
        classification="user_approved_assumption",
        source="test-only approved assumption",
        applicability="test-only",
    )
    profile = project.cap_planning_inputs.profile
    profile.product_mapping = known("JNET1")
    profile.variant = known("JGW-JNET1-915-ID")
    profile.band_and_jurisdiction = known("915 MHz test-only")
    profile.link_distance_m = known(20, "m")
    profile.node_limit = known(100, "node")
    profile.child_limit = known(16, "node")
    profile.hop_limit = known(64, "hop")
    profile.gateway_appliance_counting = known("excluded")
    profile.colocated_fixture_counting = known("distinct_managed_node_once")
    profile.redundancy = known("single_allowed_with_warning")
    profile.node_policy.LITE = CapNodeDisposition.NON_NODE
    profile.node_policy.WIFI = CapNodeDisposition.NODE
    profile.node_policy.SMART = CapNodeDisposition.NON_NODE
    profile.mode_permission = "recommend_from_approved_pool"
    project.cap_planning_inputs.candidates = [
        CapCandidateSite(
            id="cap-a",
            kind="existing_pole",
            pole_id="p0",
            mounting_confirmed=True,
            power_confirmed=True,
            backhaul_confirmed=True,
            enclosure_confirmed=True,
            indoor_outdoor="outdoor",
            survey_status="confirmed",
        )
    ]
    return project


def wifi_fixtures():
    return CatalogStore(root=ROOT / "backend" / "data" / "does-not-exist").fixtures()


# ---------------------------------------------------------------------------
# P7-DM-01 — strict report models
# ---------------------------------------------------------------------------


def test_p7_dm_01_report_models_reject_extras_nonfinite_and_project_validates_report_fields():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ReportPreferences.model_validate({"unexpected": True})
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        LastReportMetadata.model_validate(
            {
                "generated_at": FIXED_TIME.isoformat(),
                "status": "complete",
                "report_input_sha256": "a" * 64,
                "package_sha256": "b" * 64,
                "package_size_bytes": 10,
                "member_count": 1,
                "unexpected": True,
            }
        )
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ReportPackageRequest.model_validate({"unexpected": True})

    with pytest.raises(ValidationError, match="finite"):
        LastReportMetadata(
            generated_at=FIXED_TIME,
            status="complete",
            report_input_sha256="a" * 64,
            package_sha256="b" * 64,
            package_size_bytes=float("inf"),
            member_count=1,
        )
    with pytest.raises(ValidationError):
        LastReportMetadata(
            generated_at=FIXED_TIME,
            status="complete",
            report_input_sha256="a" * 64,
            package_sha256="b" * 64,
            package_size_bytes=MAX_REPORT_PACKAGE_BYTES + 1,
            member_count=1,
        )

    project = bare_project()
    assert project.schema_version == SCHEMA_VERSION == "2.7.0"
    assert isinstance(project.report_preferences, ReportPreferences)
    assert project.last_report is None
    restored = Project.model_validate(project.model_dump(mode="json"))
    assert restored.report_preferences.model_dump() == project.report_preferences.model_dump()
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Project.model_validate(
            {**project.model_dump(mode="json"), "report_preferences": {"formats": {}, "extra": 1}}
        )


# ---------------------------------------------------------------------------
# P7-MG-01 — migration to 2.7.0
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["1.0.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0", "2.5.0", "2.6.0"])
def test_p7_mg_01_migrate_prior_versions_add_empty_report_fields_losslessly(version: str):
    project = bare_project(name="Migrate Me")
    payload = project.model_dump(mode="json")
    payload["schema_version"] = version
    payload["source_references"] = {"source_sha256": "c" * 64}
    payload["recommended_layers"] = {"future": {"preserve": True}}
    payload.pop("report_preferences", None)
    payload.pop("last_report", None)
    for key in ("cap_planning_inputs", "cap_calculations", "cap_recommendations"):
        if version < "2.6.0":
            payload.pop(key, None)

    original_source = copy.deepcopy(payload["source"])
    migrated = migrate_project_payload(payload)
    assert migrated["schema_version"] == SCHEMA_VERSION == "2.7.0"
    assert migrated["software_version"] == SOFTWARE_VERSION
    assert migrated["source"] == original_source
    assert migrated["recommended_layers"] == {"future": {"preserve": True}}
    assert migrated["report_preferences"] == {}
    assert migrated["last_report"] is None
    validated = Project.model_validate(migrated)
    assert validated.report_preferences.formats.project_json is True
    assert validated.last_report is None
    assert migrate_project_payload(migrated) == migrated


def test_p7_mg_01_current_schema_migrate_is_identity():
    project = bare_project()
    payload = project.model_dump(mode="json")
    assert migrate_project_payload(payload) is payload
    assert SCHEMA_VERSION == "2.7.0"


# ---------------------------------------------------------------------------
# P7-SN / P7-ST — snapshot layers and stale omission
# ---------------------------------------------------------------------------


def test_p7_snapshot_01_separates_layers_without_mutation():
    project = bare_project()
    project.assumptions.append("test assumption")
    project.source_references["note"] = "ref"
    before = project.model_dump(mode="json")
    snapshot = build_snapshot(
        project,
        formats=ReportFormatSelection(),
        sections=ReportSectionSelection(),
        kmz_layers=project.report_preferences.kmz_layers,
        generation_time=FIXED_TIME,
    )
    assert snapshot["status"] in {"complete", "complete_with_warnings", "incomplete"}
    assert "dispositions" in snapshot
    assert snapshot["included_calculated"]["lighting"] == {}
    assert snapshot["included_calculated"]["wifi"] is None
    assert snapshot["included_calculated"]["cap"] is None
    assert "report_input_sha256" in snapshot
    assert len(snapshot["report_input_sha256"]) == 64
    assert project.model_dump(mode="json") == before
    fp = snapshot["fingerprint_payload"]
    assert "user" in fp and "calculated" in fp and "recommended" in fp
    assert "warnings" in fp and "assumptions" in fp


def test_p7_st_01_stale_lighting_wifi_cap_omitted_without_recalculation():
    project = bare_project()
    ring = _closed_ring_near_pole()
    area = CalculationArea(id="area-1", name="Road", classification="ROAD", wgs84_coordinates=ring)
    project.calculation_areas = [area]
    current_lighting_hash = lighting_calculation_input_sha256(project, area.id)
    stale_lighting_hash = "0" * 64
    assert stale_lighting_hash != current_lighting_hash
    project.lighting_calculations.results[area.id] = LightingCalculationResult(
        calculation_area_id=area.id,
        calculation_area_name=area.name,
        polygon_revision=area.calculation_state.polygon_revision,
        projected_crs="EPSG:32617",
        calculation_input_sha256=stale_lighting_hash,
        statistics=LightingStatistics(point_count=1, grid_spacing_m=2.0, average_illuminance_lux=1.0),
    )

    wifi_project = bare_project()
    wifi_project.pole_edits["p1"] = PoleEdit(pole_id="p1", fixture_type=FixtureType.WIFI)
    wifi_result = calculate_wifi_coverage(wifi_project, wifi_fixtures())
    wifi_project = apply_wifi_result(wifi_project, wifi_result)
    wifi_project.wifi_coverage.result.calculation_input_sha256 = "1" * 64
    wifi_project.wifi_coverage.state.calculation_input_sha256 = "1" * 64
    assert wifi_project.wifi_coverage.result.calculation_input_sha256 != wifi_calculation_input_sha256(wifi_project)

    cap_project = project_with_cap_inputs()
    cap_project = apply_cap_result(cap_project, calculate_cap_plan(cap_project))
    assert cap_project.cap_calculations.result is not None
    cap_project.cap_calculations.calculation_input_sha256 = "2" * 64
    assert cap_project.cap_calculations.calculation_input_sha256 != cap_input_sha256(cap_project)

    # Merge stale calculated layers onto one project for a single snapshot.
    project.pole_edits["p1"] = PoleEdit(pole_id="p1", fixture_type=FixtureType.WIFI)
    project.wifi_coverage = wifi_project.wifi_coverage
    # CAP needs matching poles/candidates — use dedicated snapshot for CAP.
    lighting_wifi_before = project.model_dump(mode="json")
    snapshot = build_snapshot(
        project,
        formats=ReportFormatSelection(),
        sections=ReportSectionSelection(),
        kmz_layers=project.report_preferences.kmz_layers,
        generation_time=FIXED_TIME,
    )
    assert snapshot["included_calculated"]["lighting"] == {}
    assert snapshot["included_calculated"]["wifi"] is None
    assert snapshot["dispositions"]["lighting"] == "stale_omitted"
    assert snapshot["dispositions"]["wifi"] == "stale_omitted"
    assert snapshot["status"] == "incomplete"
    assert any("INCOMPLETE REPORT" in item for item in snapshot["findings"])
    assert any("not recalculated" in item.lower() for item in snapshot["findings"])
    assert project.model_dump(mode="json") == lighting_wifi_before
    assert project.lighting_calculations.results[area.id].calculation_input_sha256 == stale_lighting_hash
    assert project.wifi_coverage.result is not None

    cap_before = cap_project.model_dump(mode="json")
    cap_snapshot = build_snapshot(
        cap_project,
        formats=ReportFormatSelection(),
        sections=ReportSectionSelection(),
        kmz_layers=cap_project.report_preferences.kmz_layers,
        generation_time=FIXED_TIME,
    )
    assert cap_snapshot["included_calculated"]["cap"] is None
    assert cap_snapshot["dispositions"]["cap"] == "stale_omitted"
    assert cap_snapshot["status"] == "incomplete"
    assert cap_project.model_dump(mode="json") == cap_before
    assert cap_project.cap_calculations.result is not None


# ---------------------------------------------------------------------------
# P7-FP-01 — fingerprint / byte identity
# ---------------------------------------------------------------------------


def test_p7_fp_01_significant_input_changes_fingerprint_fixed_clock_byte_identical():
    project = bare_project(name="Fingerprint Base")
    request = fixed_request()
    zip_a, manifest_a, _ = generate_report_package(project, request)
    zip_b, manifest_b, _ = generate_report_package(project, request)
    assert zip_a == zip_b
    assert manifest_a["report_input_sha256"] == manifest_b["report_input_sha256"]
    assert hashlib.sha256(zip_a).hexdigest() == hashlib.sha256(zip_b).hexdigest()

    changed = bare_project(name="Fingerprint Changed")
    _, manifest_changed, _ = generate_report_package(changed, request)
    assert manifest_changed["report_input_sha256"] != manifest_a["report_input_sha256"]

    edited = bare_project(name="Fingerprint Base")
    edited.pole_edits["p1"] = PoleEdit(pole_id="p1", fixture_type=FixtureType.SMART, height_m=9.5)
    _, manifest_edited, _ = generate_report_package(edited, request)
    assert manifest_edited["report_input_sha256"] != manifest_a["report_input_sha256"]


def test_p7_qa_01_fixed_clock_remains_byte_identical_after_delay():
    project = bare_project()
    request = fixed_request()
    package_a, _, _ = generate_report_package(project, request)
    time.sleep(2.1)
    package_b, _, _ = generate_report_package(project, request)
    assert package_a == package_b


# ---------------------------------------------------------------------------
# P7-MF-01 — manifest integrity
# ---------------------------------------------------------------------------


def test_p7_manifest_01_versions_member_hashes_status_and_tampering_detection():
    project = bare_project(name="Manifest")
    package, manifest, _ = generate_report_package(project, fixed_request())
    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["software_version"] == SOFTWARE_VERSION
    assert manifest["report_model_version"]
    assert manifest["status"] in {"complete", "complete_with_warnings", "incomplete"}
    assert "report_input_sha256" in manifest
    assert "section_dispositions" in manifest
    assert "members" in manifest
    members = _zip_members(package)
    assert "report-manifest.json" in members
    assert set(manifest["members"]) == set(members) - {"report-manifest.json"}
    for path, meta in manifest["members"].items():
        assert path in members
        assert meta["size_bytes"] == len(members[path])
        assert meta["sha256"] == hashlib.sha256(members[path]).hexdigest()

    # Tampering: flip one byte of a schedule member and recompute — hash must mismatch.
    target = next(path for path in members if path.startswith("schedules/"))
    tampered = bytearray(members[target])
    tampered[0] = (tampered[0] + 1) % 256
    assert hashlib.sha256(bytes(tampered)).hexdigest() != manifest["members"][target]["sha256"]


def test_p7_qa_02_manifest_hashes_every_payload_member_without_self_entry():
    package, manifest, _ = generate_report_package(bare_project(), fixed_request())
    members = _zip_members(package)
    assert "report-manifest.json" in members
    assert "report-manifest.json" not in manifest["members"]
    assert set(manifest["members"]) == set(members) - {"report-manifest.json"}
    for path, integrity in manifest["members"].items():
        assert integrity["size_bytes"] == len(members[path])
        assert integrity["sha256"] == hashlib.sha256(members[path]).hexdigest()


def test_p7_mf_01_preview_exposes_checklist_without_mutation():
    project = bare_project()
    before = project.model_dump(mode="json")
    preview = preview_report(project, fixed_request())
    assert preview["can_generate"] is True
    assert preview["checklist"]
    assert project.model_dump(mode="json") == before


# ---------------------------------------------------------------------------
# P7-CSV / P7-XL — schedules and injection hardening
# ---------------------------------------------------------------------------


def test_p7_csv_01_stable_schedule_names_and_formula_injection_literals():
    project = bare_project()
    project.pole_edits["p1"] = PoleEdit(
        pole_id="p1",
        engineering_notes="=CMD()",
        display_name="+Danger",
    )
    package, _, _ = generate_report_package(
        project,
        fixed_request(formats=ReportFormatSelection(xlsx_workbook=False, pdf_summary=False, presentation_model=False, engineering_kmz=False)),
    )
    members = _zip_members(package)
    expected_names = [filename for _key, filename, _title in CSV_SPECS]
    for filename in expected_names:
        path = f"schedules/{filename}"
        assert path in members
        text = members[path].decode("utf-8")
        assert text.endswith("\r\n") or "\r\n" in text
    poles_csv = members["schedules/02-poles-fixtures.csv"].decode("utf-8")
    assert safe_cell("=CMD()") == "'=CMD()"
    assert safe_cell("+Danger") == "'+Danger"
    assert "'=CMD()" in poles_csv
    assert "'+Danger" in poles_csv


def test_p7_xlsx_01_workbook_matches_safe_literal_cells():
    project = bare_project()
    project.pole_edits["p1"] = PoleEdit(pole_id="p1", engineering_notes="@SUM(A1)")
    package, _, _ = generate_report_package(
        project,
        fixed_request(formats=ReportFormatSelection(csv_schedules=False, pdf_summary=False, presentation_model=False, engineering_kmz=False, project_json=False)),
    )
    members = _zip_members(package)
    assert "workbook.xlsx" in members
    # XlsxWriter stores shared strings; confirm formula prefix is quoted literal.
    with zipfile.ZipFile(io.BytesIO(members["workbook.xlsx"])) as workbook:
        names = workbook.namelist()
        shared = workbook.read("xl/sharedStrings.xml").decode("utf-8")
    assert "'@SUM(A1)" in shared or "&apos;@SUM(A1)" in shared
    assert any(name.startswith("xl/worksheets/") for name in names)


# ---------------------------------------------------------------------------
# P7-SC — security helpers and limits
# ---------------------------------------------------------------------------


def test_p7_security_01_safe_cell_and_safe_zip_path_reject_traversal_and_oversized_cells():
    assert safe_cell("=1+1") == "'=1+1"
    assert safe_cell("-1") == "'-1"
    with pytest.raises(ReportGenerationError, match="character limit"):
        safe_cell("x" * (MAX_REPORT_CELL_CHARS + 1))
    with pytest.raises(ReportGenerationError, match="non-finite"):
        safe_cell(float("nan"))
    assert safe_zip_path("schedules", "01-project-inventory.csv") == "schedules/01-project-inventory.csv"
    with pytest.raises(ReportGenerationError, match="illegal segment"):
        safe_zip_path("..", "secret.csv")
    with pytest.raises(ReportGenerationError, match="illegal segment"):
        safe_zip_path("schedules/../etc", "passwd")
    with pytest.raises(ReportGenerationError, match="illegal segment|relative"):
        safe_zip_path("/absolute/path.csv")


def test_p7_sc_01_path_traversal_rejected_via_safe_zip_path():
    with pytest.raises(ReportGenerationError):
        safe_zip_path("a", "..", "b")


# ---------------------------------------------------------------------------
# P7-KM — engineering KMZ vs updated KML
# ---------------------------------------------------------------------------


def test_p7_kml_01_p7_kmz_01_engineering_kmz_contains_derived_or_conceptual_labels():
    project = bare_project()
    project.priority_areas = [
        PriorityArea(id="prio-1", name="Priority", wgs84_coordinates=_closed_ring_near_pole())
    ]
    package, _, _ = generate_report_package(
        project,
        fixed_request(
            formats=ReportFormatSelection(
                project_json=False,
                csv_schedules=False,
                xlsx_workbook=False,
                pdf_summary=False,
                presentation_model=False,
            )
        ),
    )
    members = _zip_members(package)
    kmz_path = next(path for path in members if path.endswith("-engineering.kmz"))
    with zipfile.ZipFile(io.BytesIO(members[kmz_path])) as kmz:
        kml = kmz.read("doc.kml").decode("utf-8")
    assert "DERIVED" in kml or "CONCEPTUAL" in kml
    assert "DERIVED" in kml
    assert "Priority" in kml


def test_p7_source_01_updated_kml_remains_cap_free():
    project = import_project("customer.kml", SIMPLE_KML)
    project.cap_planning_inputs.candidates = [
        CapCandidateSite(
            id="cap-a",
            kind="existing_pole",
            pole_id=project.source.poles[0].id,
            mounting_confirmed=True,
            power_confirmed=True,
            backhaul_confirmed=True,
            enclosure_confirmed=True,
            indoor_outdoor="outdoor",
            survey_status="confirmed",
        )
    ]
    project.cap_calculations.result = CapPlanningResult(
        projected_crs=project.projected_crs or "EPSG:32617",
        disclaimer="Distance-qualified conceptual link; not RF-predicted.",
        heuristic="test",
        selected_candidate_ids=["cap-a"],
        limits=CapPlanningLimits(
            link_distance_m=20,
            node_limit=100,
            child_limit=16,
            hop_limit=64,
            edge_evaluations=0,
            canonical_link_count=0,
            improvement_passes=1,
        ),
        result_sha256="a" * 64,
    )
    exported = export_updated_kml(project).decode("utf-8")
    # Accepted updated-KML contract stays CAP-free and report-free.
    assert "cap-a" not in exported
    assert "cap_calculations" not in exported
    assert "report-manifest" not in exported
    assert "DERIVED" not in exported
    assert "CONCEPTUAL" not in exported


# ---------------------------------------------------------------------------
# P7-PDF / P7-PR — PDF and presentation model
# ---------------------------------------------------------------------------


def test_p7_pdf_01_summary_starts_with_pdf_header():
    project = bare_project(name="PDF Project")
    package, _, _ = generate_report_package(
        project,
        fixed_request(
            formats=ReportFormatSelection(
                project_json=False,
                engineering_kmz=False,
                csv_schedules=False,
                xlsx_workbook=False,
                presentation_model=False,
            )
        ),
    )
    pdf = _zip_members(package)["summary.pdf"]
    assert pdf.startswith(b"%PDF")


def test_p7_presentation_01_model_validates_and_is_not_a_presentation():
    project = bare_project(name="Presentation")
    package, _, _ = generate_report_package(
        project,
        fixed_request(
            formats=ReportFormatSelection(
                project_json=False,
                engineering_kmz=False,
                csv_schedules=False,
                xlsx_workbook=False,
                pdf_summary=False,
            )
        ),
    )
    payload = json.loads(_zip_members(package)["presentation-model.json"].decode("utf-8"))
    assert payload["kind"] == "presentation-model"
    assert payload["presentation_generated"] is False
    assert payload["pptx_supported"] is False
    assert "NOT a presentation" in payload["label"]
    assert payload["project_id"] == project.id
    assert payload["status"] in {"complete", "complete_with_warnings", "incomplete"}


# ---------------------------------------------------------------------------
# P7-AP / P7-AT — API and atomic failure
# ---------------------------------------------------------------------------


def _temp_project_store():
    """Local tempfile store — avoids brittle system pytest basetemp ACL issues on Windows."""
    return tempfile.TemporaryDirectory(prefix="lcwa-p7-")


def test_p7_api_01_missing_project_404_and_success_returns_zip():
    with _temp_project_store() as root:
        store = ProjectStore(Path(root) / "projects")
        client = TestClient(create_app(store))
        missing = client.get("/api/projects/does-not-exist/reports/preview")
        assert missing.status_code == 404
        missing_pkg = client.post("/api/projects/does-not-exist/reports/package", json={})
        assert missing_pkg.status_code == 404

        project = bare_project(name="API Report")
        store.save(project)
        preview = client.get(f"/api/projects/{project.id}/reports/preview")
        assert preview.status_code == 200
        assert preview.json()["can_generate"] is True

        response = client.post(
            f"/api/projects/{project.id}/reports/package",
            json={
                "generation_time": FIXED_TIME.isoformat().replace("+00:00", "Z"),
                "persist_last_report_metadata": True,
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/zip")
        assert response.content[:2] == b"PK"
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            assert "report-manifest.json" in archive.namelist()

        reloaded = store.load(project.id)
        assert reloaded.last_report is not None
        assert reloaded.last_report.package_sha256 == hashlib.sha256(response.content).hexdigest()
        assert reloaded.last_report.status in {"complete", "complete_with_warnings", "incomplete"}


def test_p7_atomic_01_failure_leaves_project_unchanged(monkeypatch: pytest.MonkeyPatch):
    with _temp_project_store() as root:
        store = ProjectStore(Path(root) / "projects")
        project = bare_project(name="Atomic")
        store.save(project)
        before = store.load(project.id).model_dump(mode="json")
        client = TestClient(create_app(store))

        monkeypatch.setattr(reporting, "MAX_REPORT_TABULAR_ROWS", 0)

        response = client.post(
            f"/api/projects/{project.id}/reports/package",
            json={
                "generation_time": FIXED_TIME.isoformat().replace("+00:00", "Z"),
                "persist_last_report_metadata": True,
            },
        )
        assert response.status_code == 422
        after = store.load(project.id).model_dump(mode="json")
        assert after == before
        assert after["last_report"] is None


def test_p7_api_01_persist_false_does_not_write_last_report():
    with _temp_project_store() as root:
        store = ProjectStore(Path(root) / "projects")
        project = bare_project(name="No Persist")
        store.save(project)
        client = TestClient(create_app(store))
        response = client.post(
            f"/api/projects/{project.id}/reports/package",
            json={
                "generation_time": FIXED_TIME.isoformat().replace("+00:00", "Z"),
                "persist_last_report_metadata": False,
            },
        )
        assert response.status_code == 200
        assert store.load(project.id).last_report is None


# ---------------------------------------------------------------------------
# P7 limits — boundary+1
# ---------------------------------------------------------------------------


def test_p7_limits_01_oversize_member_or_row_limit_raises(monkeypatch: pytest.MonkeyPatch):
    project = bare_project()
    monkeypatch.setattr(reporting, "MAX_REPORT_TABULAR_ROWS", 1)
    # Header + one data row for inventory alone is already 2 logical rows in _csv_bytes check
    # when multiple schedules emit; force via schedule total or single schedule overflow.
    with pytest.raises(ReportGenerationError, match="row"):
        generate_report_package(project, fixed_request())

    monkeypatch.setattr(reporting, "MAX_REPORT_TABULAR_ROWS", 250_000)
    monkeypatch.setattr(reporting, "MAX_REPORT_MEMBER_BYTES", 64)
    with pytest.raises(ReportGenerationError, match="byte"):
        generate_report_package(project, fixed_request())

    with pytest.raises(ReportGenerationError, match="character limit"):
        safe_cell("y" * (MAX_REPORT_CELL_CHARS + 1))
