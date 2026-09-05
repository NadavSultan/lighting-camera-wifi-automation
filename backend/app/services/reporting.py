"""Phase 7 synchronous report package generation.

Builds a deterministic ZIP of selected report members from one validated project
snapshot without mutating engineering fields or recalculating results.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import tempfile
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Literal
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

from defusedxml import ElementTree as DET
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import xlsxwriter

from app.crs import project_transformers, validate_projected_metre_crs
from app.models import (
    MAX_REPORT_CELL_CHARS,
    MAX_REPORT_KML_FEATURES,
    MAX_REPORT_MEMBER_BYTES,
    MAX_REPORT_PACKAGE_BYTES,
    MAX_REPORT_PDF_TABLE_ROWS,
    MAX_REPORT_SHEET_NAME_LEN,
    MAX_REPORT_SHEETS,
    MAX_REPORT_TABULAR_ROWS,
    REPORT_MODEL_VERSION,
    SCHEMA_VERSION,
    SOFTWARE_VERSION,
    LastReportMetadata,
    PresentationModel,
    Project,
    ReportFormatSelection,
    ReportKmzLayerSelection,
    ReportManifest,
    ReportPackageRequest,
    ReportSectionSelection,
    utc_now,
    validate_report_member_path,
)
from app.services.cap_planning import cap_input_sha256, cap_result_sha256
from app.services.camera_geometry import camera_calculation_input_sha256
from app.services.kml import KmlImportError, validate_embedded_source
from app.services.lighting_calculation import lighting_calculation_input_sha256
from app.services.wifi_coverage import wifi_calculation_input_sha256

KML_NS = "http://www.opengis.net/kml/2.2"
REPORT_GENERATOR = "lcwa-report-package"
DISCLAIMER_REPORT = (
    "Report package for engineering review only. Conceptual Phase 4-6 outputs are not "
    "professionally validated photometry, verified RF design, compliance determinations, "
    "optimal layouts, or installation-ready deliverables."
)
CAMERA_DISCLAIMER = (
    "Camera geometry is included only when calculation_input_sha256 matches current "
    "geometry-significant inputs. Legacy results without a fingerprint are omitted until recalculated."
)

SectionDisposition = Literal["included", "omitted", "not_configured", "not_calculated", "stale_omitted", "disabled"]


class ReportGenerationError(ValueError):
    """Raised for 422-class report failures."""


# ---------------------------------------------------------------------------
# Public helpers (sanitization / hashing)
# ---------------------------------------------------------------------------


def safe_cell(value: Any) -> str:
    """RFC4180-friendly literal cell text with formula-injection hardening."""
    if value is None:
        text = ""
    elif isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ReportGenerationError("Report cell contains a non-finite numeric value")
        text = format(value, "g")
    elif isinstance(value, int):
        text = str(value)
    else:
        text = str(value)
    if len(text) > MAX_REPORT_CELL_CHARS:
        raise ReportGenerationError(
            f"Report cell exceeds the {MAX_REPORT_CELL_CHARS:,}-character limit"
        )
    if text and text[0] in {"=", "+", "-", "@"}:
        text = "'" + text
    return text


def safe_sheet_name(name: str, used: set[str]) -> str:
    cleaned = re.sub(r'[\[\]\*\/\\\?\:]', "_", (name or "Sheet").strip()) or "Sheet"
    cleaned = cleaned[:MAX_REPORT_SHEET_NAME_LEN]
    candidate = cleaned
    suffix = 1
    while candidate.lower() in {item.lower() for item in used}:
        tail = f"_{suffix}"
        candidate = cleaned[: MAX_REPORT_SHEET_NAME_LEN - len(tail)] + tail
        suffix += 1
        if suffix > MAX_REPORT_SHEETS:
            raise ReportGenerationError("Report workbook exceeds the unique sheet-name limit")
    used.add(candidate)
    return candidate


def safe_zip_path(*parts: str) -> str:
    segments: list[str] = []
    for part in parts:
        raw = str(part).replace("\\", "/").strip()
        for segment in raw.split("/"):
            segment = segment.strip()
            if not segment or segment in {".", ".."}:
                raise ReportGenerationError("Report ZIP path contains an illegal segment")
            if re.search(r"[\x00-\x1f]", segment):
                raise ReportGenerationError("Report ZIP path contains control characters")
            segments.append(re.sub(r"[^\w.\-]+", "_", segment, flags=re.UNICODE).strip("._") or "member")
    path = "/".join(segments)
    if path.startswith("/") or PurePosixPath(path).is_absolute():
        raise ReportGenerationError("Report ZIP path must be relative")
    return path


def _canonical_dumps(payload: Any) -> str:
    try:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ReportGenerationError("Report payload contains non-finite or non-JSON-compatible values") from exc


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_canonical(payload: Any) -> str:
    return _sha256_bytes(_canonical_dumps(payload).encode("utf-8"))


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return _ensure_utc(value).isoformat().replace("+00:00", "Z")


def _safe_project_basename(project: Project) -> str:
    base = re.sub(r"[^\w.\-]+", "_", (project.name or "project").strip(), flags=re.UNICODE)
    base = base.strip("._") or "project"
    return f"{base[:80]}-{project.id[:8]}"


def _assert_finite(value: Any, path: str = "value") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ReportGenerationError(f"Non-finite value at {path}")
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_finite(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_finite(item, f"{path}[{index}]")


# ---------------------------------------------------------------------------
# Option resolution and source integrity
# ---------------------------------------------------------------------------


def _resolve_options(
    project: Project,
    request: ReportPackageRequest | None,
) -> tuple[ReportFormatSelection, ReportSectionSelection, ReportKmzLayerSelection, bool]:
    prefs = project.report_preferences
    formats = request.formats if request and request.formats is not None else prefs.formats
    sections = request.sections if request and request.sections is not None else prefs.sections
    kmz_layers = request.kmz_layers if request and request.kmz_layers is not None else prefs.kmz_layers
    persist = True if request is None else request.persist_last_report_metadata
    return formats, sections, kmz_layers, persist


def _resolve_generation_time(
    request: ReportPackageRequest | None,
    clock: Callable[[], datetime] | None,
) -> datetime:
    if request is not None and request.generation_time is not None:
        return _ensure_utc(request.generation_time)
    if clock is not None:
        return _ensure_utc(clock())
    return _ensure_utc(utc_now())


def _validate_source_integrity(project: Project) -> None:
    if project.source.file is None:
        return
    try:
        validate_embedded_source(project)
    except KmlImportError as exc:
        raise ReportGenerationError(f"Source integrity failure: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 - surface any corrupt-source failure as 422
        raise ReportGenerationError(f"Source integrity failure: {exc}") from exc


def _portable_project_dict(project: Project) -> dict[str, Any]:
    """Portable project JSON without embedding original upload bytes."""
    payload = project.model_dump(mode="json")
    source_file = payload.get("source", {}).get("file")
    if isinstance(source_file, dict) and "content_base64" in source_file:
        source_file.pop("content_base64", None)
        source_file["content_embedded_in_report"] = False
    _assert_finite(payload, "project")
    return payload


# ---------------------------------------------------------------------------
# Snapshot / freshness policy (P7-D03 / P7-D13)
# ---------------------------------------------------------------------------


def _lighting_current_results(project: Project) -> tuple[dict[str, Any], list[str], list[str]]:
    included: dict[str, Any] = {}
    findings: list[str] = []
    warnings: list[str] = []
    area_by_id = {area.id: area for area in project.calculation_areas}
    for area_id, result in sorted(project.lighting_calculations.results.items()):
        area = area_by_id.get(area_id)
        if area is None:
            findings.append(f"Lighting result for missing area {area_id} omitted (stale orphan).")
            continue
        try:
            current_hash = lighting_calculation_input_sha256(project, area_id)
        except Exception as exc:  # noqa: BLE001
            raise ReportGenerationError(f"Lighting fingerprint failure for area {area_id}: {exc}") from exc
        result_dump = result.model_dump(mode="json")
        _assert_finite(result_dump, f"lighting.{area_id}")
        if result.calculation_input_sha256 != current_hash:
            findings.append(
                f"Lighting result for area {area_id} omitted: calculation_input_sha256 does not match current inputs."
            )
            continue
        if result.polygon_revision != area.calculation_state.polygon_revision:
            findings.append(
                f"Lighting result for area {area_id} omitted: polygon_revision does not match current area revision."
            )
            continue
        included[area_id] = result_dump
        warnings.extend(result.warnings)
    return included, findings, warnings


def _wifi_current_result(project: Project) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    findings: list[str] = []
    warnings: list[str] = []
    layer = project.wifi_coverage
    if layer.result is None:
        return None, findings, warnings
    try:
        current_hash = wifi_calculation_input_sha256(project)
    except Exception as exc:  # noqa: BLE001
        raise ReportGenerationError(f"Wi-Fi fingerprint failure: {exc}") from exc
    result_dump = layer.result.model_dump(mode="json")
    _assert_finite(result_dump, "wifi.result")
    if layer.result.calculation_input_sha256 != current_hash:
        findings.append("Wi-Fi coverage result omitted: calculation_input_sha256 does not match current inputs.")
        return None, findings, warnings
    state_hash = layer.state.calculation_input_sha256
    if state_hash is not None and state_hash != current_hash:
        findings.append("Wi-Fi coverage result omitted: layer state hash does not match current inputs.")
        return None, findings, warnings
    warnings.extend(layer.result.warnings)
    warnings.extend(layer.state.warnings)
    return result_dump, findings, warnings


def _cap_current_result(project: Project) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    findings: list[str] = []
    warnings: list[str] = []
    layer = project.cap_calculations
    if layer.result is None:
        return None, findings, warnings
    try:
        current_hash = cap_input_sha256(project)
    except Exception as exc:  # noqa: BLE001
        raise ReportGenerationError(f"CAP fingerprint failure: {exc}") from exc
    result = layer.result
    result_dump = result.model_dump(mode="json")
    _assert_finite(result_dump, "cap.result")
    if layer.calculation_input_sha256 != current_hash:
        findings.append("CAP result omitted: calculation_input_sha256 does not match current inputs.")
        return None, findings, warnings
    if not result.result_sha256 or len(result.result_sha256) != 64:
        raise ReportGenerationError("CAP result is corrupt: result_sha256 is missing or malformed")
    if cap_result_sha256(result) != result.result_sha256:
        raise ReportGenerationError(
            "CAP result payload hash mismatch: recomputed digest does not match result_sha256"
        )
    recommendations = project.cap_recommendations
    if recommendations.result_sha256 is not None and recommendations.result_sha256 != result.result_sha256:
        raise ReportGenerationError(
            "CAP hash mismatch: recommendations.result_sha256 does not match cap_calculations.result.result_sha256"
        )
    warnings.extend(result.warnings)
    warnings.extend(layer.warnings)
    return result_dump, findings, warnings


def _camera_current(project: Project) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    findings: list[str] = []
    warnings: list[str] = [CAMERA_DISCLAIMER]
    layer = project.camera_geometry
    if layer.calculated_at is None:
        return None, findings, warnings
    if not layer.footprints:
        findings.append("Camera geometry has calculated_at but no footprints; treated as not calculated.")
        return None, findings, warnings
    if layer.calculation_input_sha256 is None:
        findings.append(
            "Camera geometry omitted: calculation_input_sha256 is missing; legacy result requires recalculation."
        )
        return None, findings, warnings
    try:
        current_hash = camera_calculation_input_sha256(project)
    except Exception as exc:  # noqa: BLE001
        raise ReportGenerationError(f"Camera fingerprint failure: {exc}") from exc
    if layer.calculation_input_sha256 != current_hash:
        findings.append("Camera geometry omitted: calculation_input_sha256 does not match current inputs.")
        return None, findings, warnings
    payload = layer.model_dump(mode="json")
    _assert_finite(payload, "camera_geometry")
    for footprint in layer.footprints:
        warnings.extend(footprint.warnings)
    return payload, findings, warnings


def build_snapshot(
    project: Project,
    *,
    formats: ReportFormatSelection,
    sections: ReportSectionSelection,
    kmz_layers: ReportKmzLayerSelection,
    generation_time: datetime,
) -> dict[str, Any]:
    """Build a non-mutating report snapshot with section dispositions and status."""
    _validate_source_integrity(project)

    findings: list[str] = []
    warnings: list[str] = [DISCLAIMER_REPORT]
    blockers: list[str] = []
    dispositions: dict[str, SectionDisposition] = {}

    lighting_included, lighting_findings, lighting_warnings = _lighting_current_results(project)
    wifi_included, wifi_findings, wifi_warnings = _wifi_current_result(project)
    cap_included, cap_findings, cap_warnings = _cap_current_result(project)
    camera_included, camera_findings, camera_warnings = _camera_current(project)

    findings.extend(lighting_findings)
    findings.extend(wifi_findings)
    findings.extend(cap_findings)
    findings.extend(camera_findings)
    warnings.extend(lighting_warnings)
    warnings.extend(wifi_warnings)
    warnings.extend(cap_warnings)
    warnings.extend(camera_warnings)
    warnings.extend(w.message for w in project.warnings)

    def _section_disposition(
        enabled: bool,
        *,
        configured: bool,
        calculated: bool,
        included: bool,
        stale_omitted: bool,
    ) -> SectionDisposition:
        if not enabled:
            return "disabled"
        if not configured:
            return "not_configured"
        if stale_omitted:
            return "stale_omitted"
        if not calculated:
            return "not_calculated"
        if included:
            return "included"
        return "omitted"

    lighting_configured = bool(project.calculation_areas)
    lighting_stale = any("omitted" in item.lower() for item in lighting_findings)
    dispositions["lighting"] = _section_disposition(
        sections.lighting,
        configured=lighting_configured,
        calculated=bool(project.lighting_calculations.results),
        included=bool(lighting_included),
        stale_omitted=lighting_stale and sections.lighting,
    )

    wifi_configured = bool(project.wifi_analysis_areas) or any(
        (edit.fixture_configuration and edit.fixture_configuration.wifi_configuration)
        for edit in project.pole_edits.values()
    )
    wifi_stale = any("omitted" in item.lower() for item in wifi_findings)
    dispositions["wifi"] = _section_disposition(
        sections.wifi,
        configured=wifi_configured or project.wifi_coverage.result is not None,
        calculated=project.wifi_coverage.result is not None,
        included=wifi_included is not None,
        stale_omitted=wifi_stale and sections.wifi,
    )

    cap_stale = any("omitted" in item.lower() for item in cap_findings)
    dispositions["cap"] = _section_disposition(
        sections.cap,
        configured=bool(project.cap_planning_inputs.candidates) or project.cap_calculations.result is not None,
        calculated=project.cap_calculations.result is not None,
        included=cap_included is not None,
        stale_omitted=cap_stale and sections.cap,
    )

    camera_stale = any("omitted" in item.lower() for item in camera_findings)
    dispositions["cameras"] = _section_disposition(
        sections.cameras,
        configured=True,
        calculated=project.camera_geometry.calculated_at is not None,
        included=camera_included is not None,
        stale_omitted=camera_stale and sections.cameras,
    )
    dispositions["project_inventory"] = "included" if sections.project_inventory else "disabled"
    dispositions["poles_fixtures"] = "included" if sections.poles_fixtures else "disabled"
    dispositions["warnings_assumptions"] = "included" if sections.warnings_assumptions else "disabled"
    dispositions["validation_findings"] = "included" if sections.validation_findings else "disabled"
    dispositions["provenance"] = "included" if sections.provenance else "disabled"

    incomplete = any(
        dispositions.get(key) == "stale_omitted"
        for key in ("lighting", "wifi", "cap", "cameras")
    )
    if incomplete:
        findings.insert(
            0,
            "INCOMPLETE REPORT: one or more calculated results were omitted because they are stale "
            "relative to current fingerprints. Results were not recalculated during export.",
        )

    if findings and incomplete:
        status: Literal["complete", "complete_with_warnings", "incomplete"] = "incomplete"
    elif warnings or findings:
        status = "complete_with_warnings"
    else:
        status = "complete"

    source_sha = project.source.file.sha256 if project.source.file else None
    included_calculated = {
        "lighting": lighting_included if sections.lighting else {},
        "wifi": wifi_included if sections.wifi else None,
        "cap": cap_included if sections.cap else None,
        "camera_geometry": camera_included if sections.cameras else None,
    }
    included_recommended = {
        "cap_recommendations": project.cap_recommendations.model_dump(mode="json")
        if sections.cap and cap_included is not None
        else None,
    }

    fingerprint_payload = {
        "generator": REPORT_GENERATOR,
        "report_model_version": REPORT_MODEL_VERSION,
        "schema_version": SCHEMA_VERSION,
        "software_version": SOFTWARE_VERSION,
        "generation_time": _iso(generation_time),
        "project_id": project.id,
        "project_name": project.name,
        "source_sha256": source_sha,
        "formats": formats.model_dump(mode="json"),
        "sections": sections.model_dump(mode="json"),
        "kmz_layers": kmz_layers.model_dump(mode="json"),
        "user": {
            "pole_edits": project.pole_edits,
            "defaults": project.defaults.model_dump(mode="json"),
            "priority_areas": [area.model_dump(mode="json") for area in project.priority_areas],
            "calculation_areas": [area.model_dump(mode="json") for area in project.calculation_areas],
            "wifi_analysis_areas": [area.model_dump(mode="json") for area in project.wifi_analysis_areas],
            "cap_planning_inputs": project.cap_planning_inputs.model_dump(mode="json"),
            "layer_state": project.layer_state.model_dump(mode="json"),
        },
        "calculated": included_calculated,
        "recommended": included_recommended,
        "warnings": [w.model_dump(mode="json") for w in project.warnings],
        "assumptions": list(project.assumptions),
        "source_references": dict(project.source_references),
    }
    # Convert nested models in pole_edits to JSON-compatible form.
    fingerprint_payload["user"]["pole_edits"] = {
        key: edit.model_dump(mode="json") for key, edit in project.pole_edits.items()
    }
    report_input_sha256 = _sha256_canonical(fingerprint_payload)

    return {
        "generation_time": generation_time,
        "generation_time_iso": _iso(generation_time),
        "status": status,
        "formats": formats,
        "sections": sections,
        "kmz_layers": kmz_layers,
        "dispositions": dispositions,
        "findings": findings,
        "warnings": warnings,
        "blockers": blockers,
        "report_input_sha256": report_input_sha256,
        "source_sha256": source_sha,
        "included_calculated": included_calculated,
        "included_recommended": included_recommended,
        "safe_name": _safe_project_basename(project),
        "project_id": project.id,
        "project_name": project.name,
        "pole_count": len(project.source.poles),
        "fingerprint_payload": fingerprint_payload,
    }


# ---------------------------------------------------------------------------
# CSV schedules
# ---------------------------------------------------------------------------


CSV_SPECS: list[tuple[str, str, str]] = [
    ("project_inventory", "01-project-inventory.csv", "Project Inventory"),
    ("poles_fixtures", "02-poles-fixtures.csv", "Poles and Fixtures"),
    ("cameras", "03-cameras.csv", "Cameras"),
    ("lighting", "04-lighting.csv", "Lighting"),
    ("wifi", "05-wifi.csv", "Wi-Fi"),
    ("cap", "06-cap.csv", "CAP"),
    ("warnings_assumptions", "07-warnings-assumptions.csv", "Warnings and Assumptions"),
    ("validation_findings", "08-validation-findings.csv", "Validation Findings"),
    ("provenance", "09-provenance.csv", "Provenance"),
]


def _csv_bytes(headers: list[str], rows: list[list[Any]]) -> bytes:
    if len(rows) + 1 > MAX_REPORT_TABULAR_ROWS:
        raise ReportGenerationError(
            f"Report tabular rows exceed the {MAX_REPORT_TABULAR_ROWS:,}-row limit"
        )
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow([safe_cell(h) for h in headers])
    for row in rows:
        writer.writerow([safe_cell(cell) for cell in row])
    return buffer.getvalue().encode("utf-8")


def _effective_pole_fields(project: Project, pole) -> dict[str, Any]:
    edit = project.pole_edits.get(pole.id)
    fixture = (edit.fixture_type if edit and edit.fixture_type else project.defaults.fixture_type).value
    height = edit.height_m if edit and edit.height_m is not None else project.defaults.pole_height_m
    active = False if edit and edit.active is False else True
    lon = edit.longitude if edit and edit.longitude is not None else pole.longitude
    lat = edit.latitude if edit and edit.latitude is not None else pole.latitude
    return {
        "pole_id": pole.id,
        "sequence_index": pole.sequence_index,
        "name": edit.display_name if edit and edit.display_name else pole.name,
        "fixture_type": fixture,
        "height_m": height,
        "active": active,
        "longitude": lon,
        "latitude": lat,
        "notes": edit.engineering_notes if edit else None,
    }


def _build_schedule_rows(project: Project, snapshot: dict[str, Any]) -> dict[str, tuple[list[str], list[list[Any]]]]:
    sections: ReportSectionSelection = snapshot["sections"]
    schedules: dict[str, tuple[list[str], list[list[Any]]]] = {}

    if sections.project_inventory:
        headers = [
            "project_id", "project_name", "schema_version", "software_version",
            "mode", "pole_count", "source_filename", "source_sha256", "projected_crs", "status",
        ]
        source = project.source.file
        rows = [[
            project.id, project.name, project.schema_version, project.software_version,
            project.mode.value, len(project.source.poles),
            source.filename if source else "",
            source.sha256 if source else "",
            project.projected_crs or "",
            snapshot["status"],
        ]]
        schedules["project_inventory"] = (headers, rows)

    if sections.poles_fixtures:
        headers = [
            "pole_id", "sequence_index", "name", "fixture_type", "height_m", "active",
            "longitude", "latitude", "notes", "status",
        ]
        if not project.source.poles:
            rows = [["", "", "", "", "", "", "", "", "", "not configured"]]
        else:
            rows = []
            for pole in project.source.poles:
                fields = _effective_pole_fields(project, pole)
                rows.append([
                    fields["pole_id"], fields["sequence_index"], fields["name"], fields["fixture_type"],
                    fields["height_m"], fields["active"], fields["longitude"], fields["latitude"],
                    fields["notes"] or "", "current",
                ])
        schedules["poles_fixtures"] = (headers, rows)

    if sections.cameras:
        headers = [
            "pole_id", "camera_slot_id", "fixture_model_id", "camera_model_id", "lens_id",
            "enabled", "valid", "footprint_area_m2", "status", "notes",
        ]
        camera = snapshot["included_calculated"]["camera_geometry"]
        if camera is None:
            status = snapshot["dispositions"].get("cameras", "not_calculated")
            label = "not calculated" if status in {"not_calculated", "stale_omitted"} else "not configured"
            rows = [["", "", "", "", "", "", "", "", label, CAMERA_DISCLAIMER]]
        else:
            rows = []
            for footprint in camera.get("footprints", []):
                rows.append([
                    footprint.get("pole_id"), footprint.get("camera_slot_id"),
                    footprint.get("fixture_model_id"), footprint.get("camera_model_id"),
                    footprint.get("lens_id"), footprint.get("enabled"), footprint.get("valid"),
                    footprint.get("footprint_area_m2"), "current", CAMERA_DISCLAIMER,
                ])
            if not rows:
                rows = [["", "", "", "", "", "", "", "", "not calculated", CAMERA_DISCLAIMER]]
        schedules["cameras"] = (headers, rows)

    if sections.lighting:
        headers = [
            "calculation_area_id", "calculation_area_name", "polygon_revision",
            "point_count", "average_illuminance_lux", "minimum_illuminance_lux",
            "maximum_illuminance_lux", "calculation_input_sha256", "status", "disclaimer",
        ]
        lighting = snapshot["included_calculated"]["lighting"]
        if not lighting:
            label = "not calculated"
            if snapshot["dispositions"].get("lighting") == "stale_omitted":
                label = "stale omitted"
            elif not project.calculation_areas:
                label = "not configured"
            rows = [["", "", "", "", "", "", "", "", label,
                     "Not independently validated against AGi32 or another professional photometric reference tool."]]
        else:
            rows = []
            for area_id, result in sorted(lighting.items()):
                stats = result.get("statistics") or {}
                rows.append([
                    area_id, result.get("calculation_area_name"), result.get("polygon_revision"),
                    stats.get("point_count"), stats.get("average_illuminance_lux"),
                    stats.get("minimum_illuminance_lux"), stats.get("maximum_illuminance_lux"),
                    result.get("calculation_input_sha256"), "current",
                    result.get("disclaimer") or "",
                ])
        schedules["lighting"] = (headers, rows)

    if sections.wifi:
        headers = [
            "metric", "value", "units", "calculation_input_sha256", "status", "disclaimer",
        ]
        wifi = snapshot["included_calculated"]["wifi"]
        disclaimer = (
            "Conceptual geometric visualization only; not verified RF coverage, performance, "
            "capacity, service quality, or standards compliance."
        )
        if wifi is None:
            label = "not calculated"
            if snapshot["dispositions"].get("wifi") == "stale_omitted":
                label = "stale omitted"
            elif not project.wifi_analysis_areas and project.wifi_coverage.result is None:
                label = "not configured"
            rows = [["coverage", "", "", "", label, disclaimer]]
        else:
            stats = wifi.get("global_statistics") or {}
            digest = wifi.get("calculation_input_sha256")
            rows = [
                ["circle_count", stats.get("circle_count"), "count", digest, "current", disclaimer],
                ["union_covered_area_m2", stats.get("union_covered_area_m2"), "m2", digest, "current", disclaimer],
                ["overlap_area_m2", stats.get("overlap_area_m2"), "m2", digest, "current", disclaimer],
            ]
        schedules["wifi"] = (headers, rows)

    if sections.cap:
        headers = [
            "selected_candidate_id", "assignment_count", "link_count", "unresolved_count",
            "result_sha256", "calculation_input_sha256", "status", "disclaimer",
        ]
        cap = snapshot["included_calculated"]["cap"]
        disclaimer = (
            "Distance-qualified conceptual link; not RF-predicted. Graph-and-constraint planning "
            "only; not coverage, capacity, performance, service quality, installation feasibility, "
            "or compliance."
        )
        if cap is None:
            label = "not calculated"
            if snapshot["dispositions"].get("cap") == "stale_omitted":
                label = "stale omitted"
            rows = [["", "", "", "", "", "", label, disclaimer]]
        else:
            selected = cap.get("selected_candidate_ids") or []
            rows = [[
                ",".join(selected),
                len(cap.get("assignments") or []),
                len(cap.get("canonical_links") or []),
                len(cap.get("unresolved_node_ids") or []),
                cap.get("result_sha256"),
                project.cap_calculations.calculation_input_sha256,
                "current",
                cap.get("disclaimer") or disclaimer,
            ]]
        schedules["cap"] = (headers, rows)

    if sections.warnings_assumptions:
        headers = ["kind", "code_or_index", "severity", "message", "status"]
        rows: list[list[Any]] = []
        for warning in project.warnings:
            rows.append(["warning", warning.code, warning.severity.value, warning.message, "current"])
        for index, assumption in enumerate(project.assumptions):
            rows.append(["assumption", index, "info", assumption, "current"])
        for message in snapshot["warnings"]:
            if message in project.assumptions:
                continue
            rows.append(["report_warning", "", "warning", message, "current"])
        if not rows:
            rows = [["warning", "", "info", "none", "not configured"]]
        schedules["warnings_assumptions"] = (headers, rows)

    if sections.validation_findings:
        headers = ["finding_index", "severity", "message", "status"]
        rows = [
            [index, "warning" if "INCOMPLETE" not in message else "error", message, snapshot["status"]]
            for index, message in enumerate(snapshot["findings"])
        ]
        if not rows:
            rows = [[0, "info", "No validation findings", "complete"]]
        schedules["validation_findings"] = (headers, rows)

    if sections.provenance:
        headers = ["key", "value", "status"]
        rows = [
            ["report_model_version", REPORT_MODEL_VERSION, "current"],
            ["schema_version", SCHEMA_VERSION, "current"],
            ["software_version", SOFTWARE_VERSION, "current"],
            ["report_input_sha256", snapshot["report_input_sha256"], "current"],
            ["generation_time", snapshot["generation_time_iso"], "current"],
            ["source_sha256", snapshot["source_sha256"] or "", "current"],
        ]
        for key, value in sorted(project.source_references.items()):
            rows.append([f"source_reference.{key}", value, "current"])
        schedules["provenance"] = (headers, rows)

    total_rows = sum(len(rows) for _, rows in schedules.values())
    if total_rows > MAX_REPORT_TABULAR_ROWS:
        raise ReportGenerationError(
            f"Report tabular rows exceed the {MAX_REPORT_TABULAR_ROWS:,}-row limit"
        )
    return schedules


# ---------------------------------------------------------------------------
# XLSX workbook
# ---------------------------------------------------------------------------


def _build_workbook(
    schedules: dict[str, tuple[list[str], list[list[Any]]]],
    snapshot: dict[str, Any],
    generation_time: datetime,
) -> bytes:
    if len(schedules) > MAX_REPORT_SHEETS:
        raise ReportGenerationError(f"Report workbook exceeds the {MAX_REPORT_SHEETS}-sheet limit")
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer, {"in_memory": True, "strings_to_urls": False, "strings_to_formulas": False})
    workbook.set_properties(
        {
            "title": f"Engineering report — {snapshot['project_name']}",
            "author": "Lighting Camera WiFi Automation",
            "created": _ensure_utc(generation_time).replace(tzinfo=None),
        }
    )
    header_format = workbook.add_format({"bold": True, "bg_color": "#E8EEF5"})
    used_names: set[str] = set()
    name_by_key = {key: title for key, _filename, title in CSV_SPECS}
    for key, (headers, rows) in schedules.items():
        sheet_name = safe_sheet_name(name_by_key.get(key, key), used_names)
        worksheet = workbook.add_worksheet(sheet_name)
        for col, header in enumerate(headers):
            worksheet.write_string(0, col, safe_cell(header), header_format)
        for row_index, row in enumerate(rows, start=1):
            for col, cell in enumerate(row):
                worksheet.write_string(row_index, col, safe_cell(cell))
        worksheet.autofilter(0, 0, max(len(rows), 1), max(len(headers) - 1, 0))
        worksheet.freeze_panes(1, 0)
    workbook.close()
    data = buffer.getvalue()
    if len(data) > MAX_REPORT_MEMBER_BYTES:
        raise ReportGenerationError(
            f"workbook.xlsx exceeds the {MAX_REPORT_MEMBER_BYTES:,}-byte member limit"
        )
    return data


# ---------------------------------------------------------------------------
# Engineering KMZ (derived / conceptual only)
# ---------------------------------------------------------------------------


def _kml_el(tag: str, text: str | None = None, attrib: dict[str, str] | None = None) -> ET.Element:
    element = ET.Element(f"{{{KML_NS}}}{tag}", attrib or {})
    if text is not None:
        # ElementTree escapes on serialize; store raw Unicode text only.
        element.text = str(text)
    return element


def _add_polygon_placemark(
    folder: ET.Element,
    *,
    name: str,
    description: str,
    ring: Iterable[tuple[float, float]],
    style_url: str,
) -> None:
    placemark = _kml_el("Placemark")
    placemark.append(_kml_el("name", name))
    placemark.append(_kml_el("description", description))
    placemark.append(_kml_el("styleUrl", style_url))
    polygon = _kml_el("Polygon")
    outer = _kml_el("outerBoundaryIs")
    linear = _kml_el("LinearRing")
    coords = " ".join(f"{lon:.12g},{lat:.12g},0" for lon, lat in ring)
    linear.append(_kml_el("coordinates", coords))
    outer.append(linear)
    polygon.append(outer)
    placemark.append(polygon)
    folder.append(placemark)


def _add_point_placemark(
    folder: ET.Element,
    *,
    name: str,
    description: str,
    lon: float,
    lat: float,
    style_url: str,
) -> None:
    placemark = _kml_el("Placemark")
    placemark.append(_kml_el("name", name))
    placemark.append(_kml_el("description", description))
    placemark.append(_kml_el("styleUrl", style_url))
    point = _kml_el("Point")
    point.append(_kml_el("coordinates", f"{lon:.12g},{lat:.12g},0"))
    placemark.append(point)
    folder.append(placemark)


def _add_line_placemark(
    folder: ET.Element,
    *,
    name: str,
    description: str,
    coordinates: list[tuple[float, float]],
    style_url: str,
) -> None:
    placemark = _kml_el("Placemark")
    placemark.append(_kml_el("name", name))
    placemark.append(_kml_el("description", description))
    placemark.append(_kml_el("styleUrl", style_url))
    line = _kml_el("LineString")
    coords = " ".join(f"{lon:.12g},{lat:.12g},0" for lon, lat in coordinates)
    line.append(_kml_el("coordinates", coords))
    placemark.append(line)
    folder.append(placemark)


def _build_engineering_kmz(project: Project, snapshot: dict[str, Any]) -> bytes:
    layers: ReportKmzLayerSelection = snapshot["kmz_layers"]
    feature_count = 0

    def _count(n: int = 1) -> None:
        nonlocal feature_count
        feature_count += n
        if feature_count > MAX_REPORT_KML_FEATURES:
            raise ReportGenerationError(
                f"Engineering KMZ exceeds the {MAX_REPORT_KML_FEATURES:,}-feature limit"
            )

    root = _kml_el("kml")
    document = _kml_el("Document")
    document.append(_kml_el("name", f"{project.name} — DERIVED ENGINEERING LAYERS"))
    document.append(_kml_el(
        "description",
        "DERIVED / CONCEPTUAL layers only. Not source customer geometry. Not a design approval. "
        + DISCLAIMER_REPORT,
    ))

    def _style(style_id: str, line: str, poly: str) -> None:
        style = _kml_el("Style", attrib={"id": style_id})
        line_style = _kml_el("LineStyle")
        line_style.append(_kml_el("color", line))
        line_style.append(_kml_el("width", "2"))
        poly_style = _kml_el("PolyStyle")
        poly_style.append(_kml_el("color", poly))
        icon_style = _kml_el("IconStyle")
        icon_style.append(_kml_el("color", line))
        style.append(line_style)
        style.append(poly_style)
        style.append(icon_style)
        document.append(style)

    _style("lcwa-derived-camera", "ff0000ff", "4d0000ff")
    _style("lcwa-derived-lighting", "ff00a5ff", "4d00a5ff")
    _style("lcwa-derived-wifi", "ff00ffff", "4d00ffff")
    _style("lcwa-derived-cap", "ff00ff00", "4d00ff00")
    _style("lcwa-derived-priority", "ffaa00aa", "4daa00aa")
    _style("lcwa-derived-calc-area", "ff0088ff", "4d0088ff")
    _style("lcwa-derived-wifi-area", "ffffff00", "4dffff00")

    if layers.priority_areas:
        folder = _kml_el("Folder")
        folder.append(_kml_el("name", "DERIVED — Priority Areas (user configuration)"))
        for area in project.priority_areas:
            _count()
            _add_polygon_placemark(
                folder,
                name=f"[DERIVED] {area.name}",
                description="User priority area. DERIVED export layer; not source KML.",
                ring=area.wgs84_coordinates,
                style_url="#lcwa-derived-priority",
            )
        document.append(folder)

    if layers.calculation_areas:
        folder = _kml_el("Folder")
        folder.append(_kml_el("name", "DERIVED — Lighting Calculation Areas"))
        for area in project.calculation_areas:
            _count()
            _add_polygon_placemark(
                folder,
                name=f"[DERIVED] {area.name}",
                description="Lighting calculation area. CONCEPTUAL / DERIVED; not professionally validated.",
                ring=area.wgs84_coordinates,
                style_url="#lcwa-derived-calc-area",
            )
        document.append(folder)

    if layers.wifi_analysis_areas:
        folder = _kml_el("Folder")
        folder.append(_kml_el("name", "DERIVED — Wi-Fi Analysis Areas"))
        for area in project.wifi_analysis_areas:
            _count()
            _add_polygon_placemark(
                folder,
                name=f"[DERIVED] {area.name}",
                description="Wi-Fi analysis area. CONCEPTUAL geometry only; not verified RF.",
                ring=area.wgs84_coordinates,
                style_url="#lcwa-derived-wifi-area",
            )
        document.append(folder)

    camera = snapshot["included_calculated"]["camera_geometry"]
    if layers.camera_geometry and camera is not None:
        folder = _kml_el("Folder")
        folder.append(_kml_el("name", "DERIVED — Camera Footprints (CONCEPTUAL)"))
        for footprint in camera.get("footprints", []):
            ring = footprint.get("wgs84_coordinates")
            if not ring:
                continue
            _count()
            _add_polygon_placemark(
                folder,
                name=f"[DERIVED] camera {footprint.get('pole_id')} / {footprint.get('camera_slot_id')}",
                description=CAMERA_DISCLAIMER,
                ring=[(float(lon), float(lat)) for lon, lat in ring],
                style_url="#lcwa-derived-camera",
            )
        document.append(folder)

    lighting = snapshot["included_calculated"]["lighting"]
    if layers.lighting and lighting:
        folder = _kml_el("Folder")
        folder.append(_kml_el("name", "DERIVED — Lighting Results (CONCEPTUAL)"))
        for area_id, result in sorted(lighting.items()):
            area = next((item for item in project.calculation_areas if item.id == area_id), None)
            if area is None:
                continue
            _count()
            stats = result.get("statistics") or {}
            _add_polygon_placemark(
                folder,
                name=f"[DERIVED] lighting {result.get('calculation_area_name')}",
                description=(
                    f"CONCEPTUAL direct-lighting summary. avg={stats.get('average_illuminance_lux')} lux. "
                    "Not independently validated against AGi32."
                ),
                ring=area.wgs84_coordinates,
                style_url="#lcwa-derived-lighting",
            )
        document.append(folder)

    wifi = snapshot["included_calculated"]["wifi"]
    if layers.wifi and wifi is not None:
        folder = _kml_el("Folder")
        folder.append(_kml_el("name", "DERIVED — Wi-Fi Circles (CONCEPTUAL)"))
        for circle in wifi.get("circles", []):
            ring = circle.get("wgs84_ring")
            if not ring:
                continue
            _count()
            _add_polygon_placemark(
                folder,
                name=f"[DERIVED/CONCEPTUAL] wifi {circle.get('pole_id')}",
                description="Conceptual geometric circle only; not verified RF coverage.",
                ring=[(float(lon), float(lat)) for lon, lat in ring],
                style_url="#lcwa-derived-wifi",
            )
        document.append(folder)

    cap = snapshot["included_calculated"]["cap"]
    if layers.cap and cap is not None:
        folder = _kml_el("Folder")
        folder.append(_kml_el("name", "DERIVED — CAP Graph (CONCEPTUAL)"))
        pole_coords = {
            pole.id: (
                (edit.longitude if edit and edit.longitude is not None else pole.longitude),
                (edit.latitude if edit and edit.latitude is not None else pole.latitude),
            )
            for pole in project.source.poles
            for edit in [project.pole_edits.get(pole.id)]
        }
        candidate_coords: dict[str, tuple[float, float]] = {}
        for candidate in project.cap_planning_inputs.candidates:
            if candidate.kind == "existing_pole" and candidate.pole_id and candidate.pole_id in pole_coords:
                candidate_coords[candidate.id] = pole_coords[candidate.pole_id]
            elif candidate.wgs84_coordinate is not None:
                candidate_coords[candidate.id] = candidate.wgs84_coordinate
        for snapshot_row in cap.get("candidate_snapshots") or []:
            candidate_id = snapshot_row.get("candidate_id") or snapshot_row.get("id")
            pole_id = snapshot_row.get("source_pole_id")
            if candidate_id in candidate_coords:
                lon, lat = candidate_coords[candidate_id]
            elif pole_id in pole_coords:
                lon, lat = pole_coords[pole_id]
            else:
                continue
            _count()
            _add_point_placemark(
                folder,
                name=f"[DERIVED/CONCEPTUAL] CAP {candidate_id}",
                description=cap.get("disclaimer") or "Conceptual CAP graph vertex.",
                lon=float(lon),
                lat=float(lat),
                style_url="#lcwa-derived-cap",
            )
        id_to_xy: dict[str, tuple[float, float]] = {}
        for node in cap.get("node_snapshots") or []:
            pole_id = node.get("source_pole_id")
            if pole_id and pole_id in pole_coords:
                id_to_xy[node["id"]] = pole_coords[pole_id]
        for root in cap.get("candidate_snapshots") or []:
            cid = root.get("id")
            if cid in candidate_coords:
                id_to_xy[cid] = candidate_coords[cid]
        for link in cap.get("canonical_links") or []:
            left = id_to_xy.get(link.get("left_id", ""))
            right = id_to_xy.get(link.get("right_id", ""))
            if left is None or right is None:
                continue
            _count()
            _add_line_placemark(
                folder,
                name=f"[DERIVED/CONCEPTUAL] link {link.get('id')}",
                description="Distance-qualified conceptual link; not RF-predicted.",
                coordinates=[left, right],
                style_url="#lcwa-derived-cap",
            )
        document.append(folder)

    root.append(document)
    ET.register_namespace("", KML_NS)
    kml_bytes = DET.tostring(root, encoding="utf-8", xml_declaration=True)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo("doc.kml")
        info.date_time = _zip_datetime(snapshot["generation_time"])
        archive.writestr(info, kml_bytes)
    data = buffer.getvalue()
    if len(data) > MAX_REPORT_MEMBER_BYTES:
        raise ReportGenerationError(
            f"engineering KMZ exceeds the {MAX_REPORT_MEMBER_BYTES:,}-byte member limit"
        )
    return data


def _zip_datetime(value: datetime) -> tuple[int, int, int, int, int, int]:
    dt = _ensure_utc(value)
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


# ---------------------------------------------------------------------------
# PDF summary
# ---------------------------------------------------------------------------


def _pdf_escape(text: str) -> str:
    return (
        xml_escape(str(text), {"'": "&apos;", '"': "&quot;"})
        .replace("\n", "<br/>")
    )


def _projected_pole_points(project: Project) -> list[tuple[str, float, float]]:
    """Project poles into the project metre CRS; order by (x, y, id) for determinism."""
    if not project.projected_crs:
        raise ReportGenerationError("PDF vector overview requires a selected projected metre CRS")
    crs = validate_projected_metre_crs(project.projected_crs)
    to_proj, _ = project_transformers(crs)
    points: list[tuple[str, float, float]] = []
    for pole in project.source.poles:
        fields = _effective_pole_fields(project, pole)
        lon = float(fields["longitude"])
        lat = float(fields["latitude"])
        if not math.isfinite(lon) or not math.isfinite(lat):
            raise ReportGenerationError(f"Pole {fields['pole_id']} has non-finite coordinates")
        x, y = to_proj.transform(lon, lat)
        if not math.isfinite(x) or not math.isfinite(y):
            raise ReportGenerationError(f"Pole {fields['pole_id']} projected to a non-finite coordinate")
        points.append((str(fields["pole_id"]), float(x), float(y)))
    points.sort(key=lambda item: (item[1], item[2], item[0]))
    return points


def _build_vector_overview_drawing(project: Project) -> Drawing:
    """Deterministic local projected vector overview — no network basemap."""
    width, height = 420.0, 260.0
    margin = 24.0
    drawing = Drawing(width, height)
    drawing.add(Rect(0, 0, width, height, strokeColor=colors.HexColor("#1F2A37"), strokeWidth=1.0, fillColor=colors.HexColor("#F7F9FC")))
    drawing.add(Rect(margin, margin, width - 2 * margin, height - 2 * margin, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=0.75, fillColor=colors.white))

    nx = width - margin - 18
    ny = height - margin - 10
    drawing.add(Line(nx, ny - 18, nx, ny + 10, strokeColor=colors.HexColor("#111827"), strokeWidth=1.25))
    drawing.add(Line(nx, ny + 10, nx - 5, ny + 2, strokeColor=colors.HexColor("#111827"), strokeWidth=1.25))
    drawing.add(Line(nx, ny + 10, nx + 5, ny + 2, strokeColor=colors.HexColor("#111827"), strokeWidth=1.25))
    drawing.add(String(nx, ny + 14, "N", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#111827"), textAnchor="middle"))

    points = _projected_pole_points(project)
    plot_left, plot_bottom = margin + 8, margin + 8
    plot_w, plot_h = width - 2 * margin - 16, height - 2 * margin - 16

    if not points:
        cx, cy = plot_left + plot_w / 2, plot_bottom + plot_h / 2
        drawing.add(Line(cx - 12, cy, cx, cy + 12, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.0))
        drawing.add(Line(cx, cy + 12, cx + 12, cy, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.0))
        drawing.add(Line(cx + 12, cy, cx, cy - 12, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.0))
        drawing.add(Line(cx, cy - 12, cx - 12, cy, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.0))
        drawing.add(String(cx, cy - 28, "no poles", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#475569"), textAnchor="middle"))
        return drawing

    xs = [p[1] for p in points]
    ys = [p[2] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max_x - min_x
    span_y = max_y - min_y
    if span_x <= 1e-9:
        min_x -= 10.0
        max_x += 10.0
        span_x = max_x - min_x
    if span_y <= 1e-9:
        min_y -= 10.0
        max_y += 10.0
        span_y = max_y - min_y
    pad_x = span_x * 0.08
    pad_y = span_y * 0.08
    min_x -= pad_x
    max_x += pad_x
    min_y -= pad_y
    max_y += pad_y
    span_x = max_x - min_x
    span_y = max_y - min_y

    drawing.add(Rect(plot_left, plot_bottom, plot_w, plot_h, strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.5, fillColor=None))

    marker = colors.HexColor("#0F766E")
    for _pole_id, x_m, y_m in points:
        px = plot_left + ((x_m - min_x) / span_x) * plot_w
        py = plot_bottom + ((y_m - min_y) / span_y) * plot_h
        drawing.add(Circle(px, py, 3.2, strokeColor=marker, fillColor=marker, strokeWidth=0.5))

    crs_label = project.projected_crs or "projected CRS"
    drawing.add(String(margin + 4, 6, f"Projected overview · {crs_label}", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#334155")))
    return drawing


def _build_pdf(project: Project, snapshot: dict[str, Any], schedules: dict[str, tuple[list[str], list[list[Any]]]]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Report summary — {project.name}",
        author="Lighting Camera WiFi Automation",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReportTitle", parent=styles["Heading1"], spaceAfter=8)
    heading = ParagraphStyle("ReportHeading", parent=styles["Heading2"], spaceBefore=10, spaceAfter=6)
    body = ParagraphStyle("ReportBody", parent=styles["BodyText"], spaceAfter=4, leading=14)
    small = ParagraphStyle("ReportSmall", parent=styles["BodyText"], fontSize=8, leading=10, spaceAfter=2)

    story: list[Any] = []
    story.append(Paragraph(_pdf_escape(project.name), title_style))
    story.append(Paragraph(_pdf_escape("Engineering report summary (local package)"), heading))
    story.append(Paragraph(_pdf_escape(DISCLAIMER_REPORT), body))
    story.append(Paragraph(_pdf_escape(f"Generated (UTC): {snapshot['generation_time_iso']}"), body))
    story.append(Paragraph(_pdf_escape(f"Status: {snapshot['status']}"), body))
    story.append(Paragraph(_pdf_escape(f"Report input SHA-256: {snapshot['report_input_sha256']}"), small))

    story.append(Paragraph(_pdf_escape("Integrity"), heading))
    story.append(Paragraph(_pdf_escape(
        f"Source SHA-256: {snapshot['source_sha256'] or 'none'}; schema {SCHEMA_VERSION}; "
        f"software {SOFTWARE_VERSION}; model {REPORT_MODEL_VERSION}."
    ), body))

    story.append(Paragraph(_pdf_escape("Inventory"), heading))
    story.append(Paragraph(_pdf_escape(
        f"Poles: {snapshot['pole_count']}; priority areas: {len(project.priority_areas)}; "
        f"calculation areas: {len(project.calculation_areas)}; "
        f"Wi-Fi analysis areas: {len(project.wifi_analysis_areas)}; "
        f"CAP candidates: {len(project.cap_planning_inputs.candidates)}."
    ), body))

    story.append(Paragraph(_pdf_escape("Subsystem summaries"), heading))
    for key in ("cameras", "lighting", "wifi", "cap"):
        disposition = snapshot["dispositions"].get(key, "omitted")
        story.append(Paragraph(_pdf_escape(f"{key}: {disposition}"), body))

    story.append(Paragraph(_pdf_escape("Validation / limitations"), heading))
    finding_rows = snapshot["findings"][:MAX_REPORT_PDF_TABLE_ROWS]
    if not finding_rows:
        story.append(Paragraph(_pdf_escape("No validation findings."), body))
    else:
        for message in finding_rows:
            story.append(Paragraph(_pdf_escape(f"• {message}"), small))
        omitted = len(snapshot["findings"]) - len(finding_rows)
        if omitted > 0:
            story.append(Paragraph(_pdf_escape(f"… {omitted} additional findings omitted from PDF table."), small))
    story.append(Paragraph(_pdf_escape(
        "Limitations: no online basemap; no macros/hyperlinks/external images; "
        "conceptual outputs remain conceptual."
    ), body))

    story.append(Paragraph(_pdf_escape("Provenance"), heading))
    story.append(Paragraph(_pdf_escape(
        f"Generator {REPORT_GENERATOR}; project id {project.id}."
    ), body))

    story.append(Paragraph(_pdf_escape("Local vector overview"), heading))
    story.append(Paragraph(_pdf_escape(
        "Deterministic local projected vector overview of pole positions (no online basemap)."
    ), body))
    story.append(_build_vector_overview_drawing(project))
    story.append(Spacer(1, 8))

    if "project_inventory" in schedules:
        story.append(Paragraph(_pdf_escape("Schedule digest"), heading))
        headers, rows = schedules["project_inventory"]
        digest = [headers] + rows[: min(5, MAX_REPORT_PDF_TABLE_ROWS)]
        digest_table = Table(
            [[_pdf_escape(str(cell)) for cell in row] for row in digest],
            colWidths=[22 * mm] * min(len(headers), 6),
        )
        digest_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        story.append(digest_table)

    class _DeterministicCanvas(Canvas):
        def __init__(self, *args, **kwargs):
            kwargs["invariant"] = 1
            super().__init__(*args, **kwargs)

    doc.build(story, canvasmaker=_DeterministicCanvas)
    data = buffer.getvalue()
    # ReportLab may still emit a non-stable trailer /ID; pin it to the report fingerprint.
    digest = snapshot["report_input_sha256"]
    token = digest[:32].encode("ascii")
    data = re.sub(
        rb"/ID\s*\[[^\]]+\]",
        b"/ID\n[<" + token + b"><" + token + b">]",
        data,
        count=1,
    )
    if len(data) > MAX_REPORT_MEMBER_BYTES:
        raise ReportGenerationError(
            f"summary.pdf exceeds the {MAX_REPORT_MEMBER_BYTES:,}-byte member limit"
        )
    return data


# ---------------------------------------------------------------------------
# Presentation model (future input only)
# ---------------------------------------------------------------------------


def _build_presentation_model(project: Project, snapshot: dict[str, Any]) -> bytes:
    payload = {
        "kind": "presentation-model",
        "label": "Structured future presentation input — NOT a presentation",
        "presentation_generated": False,
        "pptx_supported": False,
        "report_model_version": REPORT_MODEL_VERSION,
        "schema_version": SCHEMA_VERSION,
        "software_version": SOFTWARE_VERSION,
        "project_id": project.id,
        "project_name": project.name,
        "generation_time": snapshot["generation_time_iso"],
        "status": snapshot["status"],
        "report_input_sha256": snapshot["report_input_sha256"],
        "section_dispositions": snapshot["dispositions"],
        "warnings": snapshot["warnings"],
        "findings": snapshot["findings"],
        "inventory": {
            "pole_count": snapshot["pole_count"],
            "priority_area_count": len(project.priority_areas),
            "calculation_area_count": len(project.calculation_areas),
            "wifi_analysis_area_count": len(project.wifi_analysis_areas),
            "cap_candidate_count": len(project.cap_planning_inputs.candidates),
        },
        "subsystems": {
            "lighting_included_area_ids": sorted((snapshot["included_calculated"]["lighting"] or {}).keys()),
            "wifi_included": snapshot["included_calculated"]["wifi"] is not None,
            "cap_included": snapshot["included_calculated"]["cap"] is not None,
            "camera_included": snapshot["included_calculated"]["camera_geometry"] is not None,
        },
        "disclaimer": DISCLAIMER_REPORT,
    }
    model = PresentationModel.model_validate(payload)
    data = (
        json.dumps(model.model_dump(mode="json"), indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    if len(data) > MAX_REPORT_MEMBER_BYTES:
        raise ReportGenerationError(
            f"presentation-model.json exceeds the {MAX_REPORT_MEMBER_BYTES:,}-byte member limit"
        )
    return data


# ---------------------------------------------------------------------------
# Package assembly
# ---------------------------------------------------------------------------


def _write_member(
    members: dict[str, bytes],
    path: str,
    data: bytes,
) -> None:
    if path in members:
        raise ReportGenerationError(f"Duplicate report ZIP member path: {path}")
    if len(data) > MAX_REPORT_MEMBER_BYTES:
        raise ReportGenerationError(
            f"Report member {path} exceeds the {MAX_REPORT_MEMBER_BYTES:,}-byte limit"
        )
    # Boundary+1 fails atomically: exact limit is allowed; over fails.
    members[path] = data


def _assemble_zip(members: dict[str, bytes], generation_time: datetime) -> bytes:
    buffer = io.BytesIO()
    date_time = _zip_datetime(generation_time)
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in sorted(members.items()):
            info = zipfile.ZipInfo(path)
            info.date_time = date_time
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    package = buffer.getvalue()
    if len(package) > MAX_REPORT_PACKAGE_BYTES:
        raise ReportGenerationError(
            f"Report package exceeds the {MAX_REPORT_PACKAGE_BYTES:,}-byte limit"
        )
    return package


def validate_report_package_integrity(package: bytes, manifest: ReportManifest) -> None:
    """Reopen a completed package and verify its non-circular manifest contract."""
    manifest_path = "report-manifest.json"
    try:
        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            names = [info.filename for info in archive.infolist()]
            if len(names) != len(set(names)):
                raise ReportGenerationError(
                    "Final report ZIP integrity validation found duplicate member names"
                )

            for path in names:
                if path == manifest_path:
                    continue
                try:
                    validate_report_member_path(path)
                except ValueError as exc:
                    raise ReportGenerationError(
                        f"Final report ZIP integrity validation found unsafe path: {path!r}"
                    ) from exc

            if manifest_path not in names:
                raise ReportGenerationError(
                    "Final report ZIP integrity validation found missing report-manifest.json"
                )

            payload_paths = set(names) - {manifest_path}
            declared_paths = set(manifest.members)
            missing_paths = sorted(declared_paths - payload_paths)
            if missing_paths:
                raise ReportGenerationError(
                    "Final report ZIP integrity validation found missing payload members: "
                    + ", ".join(missing_paths)
                )
            extra_paths = sorted(payload_paths - declared_paths)
            if extra_paths:
                raise ReportGenerationError(
                    "Final report ZIP integrity validation found extra payload members: "
                    + ", ".join(extra_paths)
                )

            for path, integrity in manifest.members.items():
                data = archive.read(path)
                if len(data) != integrity.size_bytes:
                    raise ReportGenerationError(
                        f"Final report ZIP integrity validation found size mismatch for {path}"
                    )
                if _sha256_bytes(data) != integrity.sha256:
                    raise ReportGenerationError(
                        f"Final report ZIP integrity validation found SHA-256 mismatch for {path}"
                    )
    except zipfile.BadZipFile as exc:
        raise ReportGenerationError(
            "Final report ZIP integrity validation could not reopen the completed package"
        ) from exc


def preview_report(project: Project, request: ReportPackageRequest | None = None) -> dict:
    """Return checklist/status/blockers/section dispositions without mutating project or writing files."""
    formats, sections, kmz_layers, _persist = _resolve_options(project, request)
    generation_time = _resolve_generation_time(request, None)
    try:
        # Work on a deep copy so accidental mutation cannot touch the caller's project.
        snapshot = build_snapshot(
            deepcopy(project),
            formats=formats,
            sections=sections,
            kmz_layers=kmz_layers,
            generation_time=generation_time,
        )
        checklist = []
        for key, _filename, title in CSV_SPECS:
            checklist.append({
                "section": key,
                "title": title,
                "enabled": bool(getattr(sections, key)),
                "disposition": snapshot["dispositions"].get(key, "omitted"),
            })
        format_checklist = [
            {"format": name, "enabled": bool(getattr(formats, name))}
            for name in (
                "project_json", "engineering_kmz", "csv_schedules",
                "xlsx_workbook", "pdf_summary", "presentation_model",
            )
        ]
        return {
            "status": snapshot["status"],
            "checklist": checklist,
            "formats": format_checklist,
            "blockers": snapshot["blockers"],
            "section_dispositions": snapshot["dispositions"],
            "warnings": snapshot["warnings"],
            "validation_findings": snapshot["findings"],
            "report_input_sha256": snapshot["report_input_sha256"],
            "generation_time": snapshot["generation_time_iso"],
            "can_generate": len(snapshot["blockers"]) == 0,
            "disclaimer": DISCLAIMER_REPORT,
        }
    except ReportGenerationError as exc:
        return {
            "status": "incomplete",
            "checklist": [],
            "formats": [],
            "blockers": [str(exc)],
            "section_dispositions": {},
            "warnings": [DISCLAIMER_REPORT],
            "validation_findings": [],
            "report_input_sha256": None,
            "generation_time": _iso(generation_time),
            "can_generate": False,
            "disclaimer": DISCLAIMER_REPORT,
        }


def _encode_manifest(manifest: dict[str, Any]) -> bytes:
    return (json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def generate_report_package(
    project: Project,
    request: ReportPackageRequest | None = None,
    *,
    clock: Callable[[], datetime] | None = None,
) -> tuple[bytes, dict, LastReportMetadata | None]:
    """
    Synchronously build the ZIP package.
    Returns (zip_bytes, manifest_dict, last_report_metadata_or_none).
    Does NOT mutate project in place for engineering fields. May return LastReportMetadata for caller to attach if persist requested.
    Failures must leave no partial temp artifacts (use tempfile.TemporaryDirectory, clean on failure).
    Fixed clock: if request.generation_time set, use it; elif clock provided use clock(); else utc_now().
    ZIP member timestamps must be normalized for determinism when using fixed generation_time.
    """
    formats, sections, kmz_layers, persist = _resolve_options(project, request)
    generation_time = _resolve_generation_time(request, clock)
    working = deepcopy(project)

    with tempfile.TemporaryDirectory(prefix="lcwa-report-") as temp_dir:
        try:
            snapshot = build_snapshot(
                working,
                formats=formats,
                sections=sections,
                kmz_layers=kmz_layers,
                generation_time=generation_time,
            )
            if snapshot["blockers"]:
                raise ReportGenerationError("; ".join(snapshot["blockers"]))

            members: dict[str, bytes] = {}
            schedules = _build_schedule_rows(working, snapshot)

            if formats.project_json:
                project_bytes = (
                    json.dumps(_portable_project_dict(working), indent=2, sort_keys=True, allow_nan=False)
                    + "\n"
                ).encode("utf-8")
                _write_member(members, safe_zip_path("project", f"{snapshot['safe_name']}.json"), project_bytes)

            if formats.engineering_kmz:
                _write_member(
                    members,
                    safe_zip_path("engineering", f"{snapshot['safe_name']}-engineering.kmz"),
                    _build_engineering_kmz(working, snapshot),
                )

            if formats.csv_schedules:
                filename_by_key = {key: filename for key, filename, _title in CSV_SPECS}
                for key, (headers, rows) in schedules.items():
                    _write_member(
                        members,
                        safe_zip_path("schedules", filename_by_key[key]),
                        _csv_bytes(headers, rows),
                    )

            if formats.xlsx_workbook:
                _write_member(
                    members,
                    safe_zip_path("workbook.xlsx"),
                    _build_workbook(schedules, snapshot, generation_time),
                )

            if formats.pdf_summary:
                _write_member(members, safe_zip_path("summary.pdf"), _build_pdf(working, snapshot, schedules))

            if formats.presentation_model:
                _write_member(
                    members,
                    safe_zip_path("presentation-model.json"),
                    _build_presentation_model(working, snapshot),
                )

            # Manifest always included on success and hashes every non-manifest payload member.
            manifest_path = safe_zip_path("report-manifest.json")
            sibling_hashes = {
                path: {"sha256": _sha256_bytes(data), "size_bytes": len(data)}
                for path, data in sorted(members.items())
            }
            included_sections = [
                key for key, value in snapshot["dispositions"].items() if value == "included"
            ]
            omitted_sections = [
                key for key, value in snapshot["dispositions"].items() if value != "included"
            ]
            manifest = ReportManifest(
                generator=REPORT_GENERATOR,
                project_id=working.id,
                project_name=working.name,
                generation_time=generation_time,
                status=snapshot["status"],
                report_input_sha256=snapshot["report_input_sha256"],
                source_sha256=snapshot["source_sha256"],
                formats=formats,
                sections=sections,
                kmz_layers=kmz_layers,
                section_dispositions=snapshot["dispositions"],
                included_sections=included_sections,
                omitted_sections=omitted_sections,
                warnings=snapshot["warnings"],
                validation_findings=snapshot["findings"],
                members=sibling_hashes,
                disclaimer=DISCLAIMER_REPORT,
            )
            written_manifest = manifest.model_dump(mode="json")
            manifest_bytes = _encode_manifest(written_manifest)
            _write_member(members, manifest_path, manifest_bytes)

            # Stage members under the isolated temp directory before packaging.
            for path, data in members.items():
                target_path = Path(temp_dir).joinpath(*PurePosixPath(path).parts)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(data)

            package = _assemble_zip(members, generation_time)
            validate_report_package_integrity(package, manifest)
            package_sha = _sha256_bytes(package)
            metadata: LastReportMetadata | None = None
            if persist:
                metadata = LastReportMetadata(
                    generated_at=generation_time,
                    status=snapshot["status"],
                    report_input_sha256=snapshot["report_input_sha256"],
                    package_sha256=package_sha,
                    package_size_bytes=len(package),
                    member_count=len(members),
                    member_sha256={path: _sha256_bytes(data) for path, data in members.items()},
                    included_sections=included_sections,
                    omitted_sections=omitted_sections,
                    warnings=list(snapshot["warnings"]),
                    validation_finding_count=len(snapshot["findings"]),
                )
            return package, written_manifest, metadata
        except Exception:
            # TemporaryDirectory removes all staged artifacts on exit.
            raise
