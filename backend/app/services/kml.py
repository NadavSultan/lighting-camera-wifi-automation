from __future__ import annotations

import base64
import hashlib
import io
import math
import posixpath
import statistics
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Iterable

from defusedxml import ElementTree as DET
from pyproj import CRS, Transformer
from xml.etree import ElementTree as ET

from app.models import (
    FixtureType,
    OperatingMode,
    PoleEdit,
    Project,
    ProjectWarning,
    SourceFile,
    SourceLayer,
    SourcePole,
    WarningSeverity,
)


KML_NS = "http://www.opengis.net/kml/2.2"
NS = {"k": KML_NS}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_KMZ_ENTRIES = 256
MAX_KMZ_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200
NEAR_DUPLICATE_METRES = 0.5
OUTLIER_METRES = 5000.0


class KmlImportError(ValueError):
    pass


@dataclass(frozen=True)
class KmlPayload:
    uploaded_bytes: bytes
    kml_bytes: bytes
    filename: str
    media_type: str
    kml_entry: str | None


def _safe_filename(filename: str) -> str:
    name = filename.replace("\\", "/").split("/")[-1].strip()
    if not name or name in {".", ".."}:
        raise KmlImportError("A valid source filename is required")
    return name


def _read_payload(filename: str, content: bytes) -> KmlPayload:
    filename = _safe_filename(filename)
    if not content:
        raise KmlImportError("The uploaded file is empty")
    if len(content) > MAX_UPLOAD_BYTES:
        raise KmlImportError("The uploaded file exceeds the 50 MB Phase 1 limit")
    suffix = PurePosixPath(filename).suffix.lower()
    if suffix == ".kml":
        return KmlPayload(content, content, filename, "application/vnd.google-earth.kml+xml", None)
    if suffix != ".kmz":
        raise KmlImportError("Only .kml and .kmz files are supported")

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_KMZ_ENTRIES:
                raise KmlImportError("KMZ contains too many archive entries")
            total = 0
            kml_entries: list[str] = []
            for entry in entries:
                normalized = posixpath.normpath(entry.filename.replace("\\", "/"))
                if normalized.startswith("../") or normalized.startswith("/") or normalized == "..":
                    raise KmlImportError("KMZ contains an unsafe archive path")
                total += entry.file_size
                if total > MAX_KMZ_UNCOMPRESSED_BYTES:
                    raise KmlImportError("KMZ uncompressed content exceeds the 100 MB limit")
                if entry.compress_size and entry.file_size / entry.compress_size > MAX_COMPRESSION_RATIO:
                    raise KmlImportError("KMZ contains an unsafe compression ratio")
                if entry.filename.lower().endswith(".kml"):
                    kml_entries.append(entry.filename)
            if not kml_entries:
                raise KmlImportError("KMZ does not contain a KML document")
            selected = next((name for name in kml_entries if name.lower() == "doc.kml"), kml_entries[0])
            return KmlPayload(content, archive.read(selected), filename, "application/vnd.google-earth.kmz", selected)
    except zipfile.BadZipFile as exc:
        raise KmlImportError("KMZ is not a valid ZIP archive") from exc


def _parse_root(kml_bytes: bytes) -> ET.Element:
    try:
        root = DET.fromstring(kml_bytes)
    except Exception as exc:
        raise KmlImportError(f"KML XML could not be parsed: {exc}") from exc
    if root.tag != f"{{{KML_NS}}}kml":
        raise KmlImportError("The document is not an OGC KML 2.2 file")
    return root


def choose_utm_crs(longitudes: Iterable[float], latitudes: Iterable[float]) -> str | None:
    lon_values = list(longitudes)
    lat_values = list(latitudes)
    if not lon_values:
        return None
    lon = statistics.median(lon_values)
    lat = statistics.median(lat_values)
    zone = max(1, min(60, math.floor((lon + 180) / 6) + 1))
    return f"EPSG:{32600 + zone if lat >= 0 else 32700 + zone}"


def _folder_placemarks(container: ET.Element, path: list[str]):
    for child in list(container):
        local = child.tag.rsplit("}", 1)[-1]
        if local == "Folder":
            folder_name = child.findtext("k:name", default="", namespaces=NS).strip()
            yield from _folder_placemarks(child, [*path, folder_name] if folder_name else path)
        elif local == "Document":
            yield from _folder_placemarks(child, path)
        elif local == "Placemark":
            yield child, path


def _extended_data(placemark: ET.Element) -> dict[str, str]:
    values: dict[str, str] = {}
    for data in placemark.findall(".//k:ExtendedData/k:Data", NS):
        name = data.get("name")
        if name:
            values[name] = data.findtext("k:value", default="", namespaces=NS)
    for data in placemark.findall(".//k:ExtendedData//k:SimpleData", NS):
        name = data.get("name")
        if name:
            values[name] = data.text or ""
    return values


def _style_colors(root: ET.Element) -> dict[str, str]:
    result: dict[str, str] = {}
    for style in root.findall(".//k:Style", NS):
        style_id = style.get("id")
        color = style.findtext("k:IconStyle/k:color", default="", namespaces=NS).strip()
        if style_id and color:
            result[f"#{style_id}"] = color
    for style_map in root.findall(".//k:StyleMap", NS):
        style_id = style_map.get("id")
        normal = style_map.find("k:Pair[k:key='normal']/k:styleUrl", NS)
        if style_id and normal is not None and normal.text in result:
            result[f"#{style_id}"] = result[normal.text]
    return result


def import_project(filename: str, content: bytes, project_name: str | None = None) -> Project:
    payload = _read_payload(filename, content)
    root = _parse_root(payload.kml_bytes)
    document = root.find("k:Document", NS)
    if document is None:
        raise KmlImportError("KML must contain a Document")

    document_name = document.findtext("k:name", default="", namespaces=NS).strip() or None
    style_colors = _style_colors(root)
    warnings: list[ProjectWarning] = []
    poles: list[SourcePole] = []
    unsupported = 0
    used_pole_ids: set[str] = set()

    for index, (placemark, folder_path) in enumerate(_folder_placemarks(document, [])):
        point = placemark.find("k:Point", NS)
        if point is None:
            unsupported += 1
            name = placemark.findtext("k:name", default=f"Placemark {index + 1}", namespaces=NS)
            warnings.append(ProjectWarning(
                code="unsupported_geometry",
                message=f"Placemark '{name}' is not a Point and was retained only in the source file.",
                details={"placemark_index": index},
            ))
            continue
        raw = point.findtext("k:coordinates", default="", namespaces=NS).strip()
        first_coordinate = raw.split()[0] if raw else ""
        parts = [part.strip() for part in first_coordinate.split(",")]
        try:
            if len(parts) < 2:
                raise ValueError("missing longitude or latitude")
            lon = float(parts[0])
            lat = float(parts[1])
            altitude = float(parts[2]) if len(parts) > 2 and parts[2] != "" else None
            if not math.isfinite(lon) or not math.isfinite(lat) or (altitude is not None and not math.isfinite(altitude)):
                raise ValueError("coordinate contains a non-finite number")
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                raise ValueError("coordinate is outside WGS84 bounds")
        except ValueError as exc:
            warnings.append(ProjectWarning(
                code="malformed_coordinate",
                severity=WarningSeverity.ERROR,
                message=f"Placemark {index + 1} has an invalid coordinate and was not imported: {exc}.",
                details={"raw_coordinates": raw, "folder_path": folder_path},
            ))
            continue
        if len(raw.split()) > 1:
            warnings.append(ProjectWarning(
                code="multi_coordinate_point",
                message=f"Point placemark {index + 1} contains multiple coordinate tuples; only the first was imported.",
            ))

        name = placemark.findtext("k:name", default=f"Pole {len(poles) + 1}", namespaces=NS)
        source_id = placemark.get("id")
        identity = "\x1f".join([payload.filename, *folder_path, name, first_coordinate, str(index)])
        generated_id = f"pole-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"
        pole_id = source_id or generated_id
        if pole_id in used_pole_ids:
            if source_id:
                warnings.append(ProjectWarning(
                    code="duplicate_placemark_id",
                    message=f"Placemark ID '{source_id}' is duplicated; a unique internal pole ID was assigned without changing the source.",
                    details={"source_placemark_id": source_id, "placemark_index": index},
                ))
            pole_id = generated_id
            collision = 2
            while pole_id in used_pole_ids:
                pole_id = f"{generated_id}-{collision}"
                collision += 1
        used_pole_ids.add(pole_id)
        style_url = placemark.findtext("k:styleUrl", default="", namespaces=NS).strip() or None
        inline_style_color = placemark.findtext("k:Style/k:IconStyle/k:color", default="", namespaces=NS).strip() or None
        poles.append(SourcePole(
            id=pole_id,
            sequence_index=index,
            source_placemark_id=source_id,
            name=name,
            folder_path=folder_path,
            description=placemark.findtext("k:description", default="", namespaces=NS),
            extended_data=_extended_data(placemark),
            source_style_url=style_url,
            source_style_color=inline_style_color or style_colors.get(style_url or ""),
            longitude=lon,
            latitude=lat,
            altitude_m=altitude,
            raw_coordinates=first_coordinate,
        ))

    if not poles:
        raise KmlImportError("No valid Point placemarks were found")
    if not warnings:
        warnings.append(ProjectWarning(
            code="import_validated",
            severity=WarningSeverity.INFO,
            message=f"Imported {len(poles)} point placemarks without geometry or coordinate errors.",
        ))

    projected_crs = choose_utm_crs((p.longitude for p in poles), (p.latitude for p in poles))
    _append_coordinate_warnings(poles, projected_crs, warnings)
    source_file = SourceFile(
        filename=payload.filename,
        media_type=payload.media_type,
        sha256=hashlib.sha256(content).hexdigest(),
        size_bytes=len(content),
        imported_at=datetime.now(timezone.utc),
        kml_entry=payload.kml_entry,
        content_base64=base64.b64encode(content).decode("ascii"),
    )
    return Project(
        name=project_name or document_name or PurePosixPath(payload.filename).stem,
        mode=OperatingMode.EXISTING_POLES,
        proposed_layout_authorized=False,
        projected_crs=projected_crs,
        source=SourceLayer(
            file=source_file,
            document_name=document_name,
            poles=poles,
            unsupported_geometry_count=unsupported,
        ),
        warnings=warnings,
        source_references={"customer_layout": payload.filename},
    )


def validate_embedded_source(project: Project) -> None:
    source_file = project.source.file
    if source_file is None:
        if project.source.poles:
            raise KmlImportError("Project has source poles but no embedded customer file")
        return
    content = base64.b64decode(source_file.content_base64, validate=True)
    reparsed = import_project(source_file.filename, content)
    if source_file.media_type != reparsed.source.file.media_type or source_file.kml_entry != reparsed.source.file.kml_entry:
        raise KmlImportError("Embedded customer file metadata does not match its KML/KMZ content")
    if (
        project.source.document_name != reparsed.source.document_name
        or project.source.poles != reparsed.source.poles
        or project.source.unsupported_geometry_count != reparsed.source.unsupported_geometry_count
        or project.projected_crs != reparsed.projected_crs
    ):
        raise KmlImportError("Original customer source records do not match the embedded KML/KMZ")


def _append_coordinate_warnings(poles: list[SourcePole], projected_crs: str | None, warnings: list[ProjectWarning]) -> None:
    exact: dict[tuple[float, float], list[str]] = defaultdict(list)
    for pole in poles:
        exact[(pole.longitude, pole.latitude)].append(pole.id)
    for coordinate, ids in exact.items():
        if len(ids) > 1:
            warnings.append(ProjectWarning(
                code="duplicate_coordinate",
                message=f"{len(ids)} poles share the exact coordinate {coordinate[0]}, {coordinate[1]}.",
                pole_ids=ids,
            ))

    if not projected_crs:
        return
    transformer = Transformer.from_crs("EPSG:4326", projected_crs, always_xy=True)
    projected = [(pole, *transformer.transform(pole.longitude, pole.latitude)) for pole in poles]
    median_x = statistics.median(item[1] for item in projected)
    median_y = statistics.median(item[2] for item in projected)
    for pole, x, y in projected:
        distance = math.hypot(x - median_x, y - median_y)
        if distance > OUTLIER_METRES:
            warnings.append(ProjectWarning(
                code="geographic_outlier",
                message=f"Pole '{pole.name}' is {distance:.0f} m from the project median and may be geographically suspicious.",
                pole_ids=[pole.id],
                details={"distance_m": round(distance, 3)},
            ))
    for left_index, (left, lx, ly) in enumerate(projected):
        for right, rx, ry in projected[left_index + 1:]:
            distance = math.hypot(lx - rx, ly - ry)
            if 0 < distance <= NEAR_DUPLICATE_METRES:
                warnings.append(ProjectWarning(
                    code="near_duplicate_coordinate",
                    message=f"Poles '{left.name}' and '{right.name}' are {distance:.2f} m apart.",
                    pole_ids=[left.id, right.id],
                    details={"distance_m": round(distance, 3)},
                ))


def _source_kml_bytes(project: Project) -> bytes:
    source = project.source.file
    if source is None:
        raise KmlImportError("Project has no source KML/KMZ")
    uploaded = base64.b64decode(source.content_base64, validate=True)
    if source.media_type.endswith("kmz"):
        with zipfile.ZipFile(io.BytesIO(uploaded)) as archive:
            if not source.kml_entry:
                raise KmlImportError("KMZ project is missing its KML entry reference")
            return archive.read(source.kml_entry)
    return uploaded


def _ensure_export_styles(document: ET.Element) -> None:
    styles = {
        FixtureType.LITE: "ff0000ff",
        FixtureType.WIFI: "ff00ffff",
        FixtureType.SMART: "ffff0000",
    }
    for fixture, color in styles.items():
        style_id = f"lcwa-{fixture.value.lower()}"
        existing = document.find(f"k:Style[@id='{style_id}']", NS)
        if existing is not None:
            continue
        style = ET.Element(f"{{{KML_NS}}}Style", {"id": style_id})
        icon_style = ET.SubElement(style, f"{{{KML_NS}}}IconStyle")
        ET.SubElement(icon_style, f"{{{KML_NS}}}color").text = color
        ET.SubElement(icon_style, f"{{{KML_NS}}}scale").text = "1.2"
        icon = ET.SubElement(icon_style, f"{{{KML_NS}}}Icon")
        ET.SubElement(icon, f"{{{KML_NS}}}href").text = "https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
        document.insert(0, style)


def _set_extended_value(placemark: ET.Element, name: str, value: str) -> None:
    extended = placemark.find("k:ExtendedData", NS)
    if extended is None:
        extended = ET.SubElement(placemark, f"{{{KML_NS}}}ExtendedData")
    for data in extended.findall("k:Data", NS):
        if data.get("name") == name:
            value_element = data.find("k:value", NS)
            if value_element is None:
                value_element = ET.SubElement(data, f"{{{KML_NS}}}value")
            value_element.text = value
            return
    data = ET.SubElement(extended, f"{{{KML_NS}}}Data", {"name": name})
    ET.SubElement(data, f"{{{KML_NS}}}value").text = value


def export_updated_kml(project: Project) -> bytes:
    root = _parse_root(_source_kml_bytes(project))
    document = root.find("k:Document", NS)
    if document is None:
        raise KmlImportError("Source KML has no Document")
    _ensure_export_styles(document)
    source_by_sequence = {pole.sequence_index: pole for pole in project.source.poles}

    for sequence, (placemark, _folder_path) in enumerate(_folder_placemarks(document, [])):
        source_pole = source_by_sequence.get(sequence)
        if source_pole is None or placemark.find("k:Point", NS) is None:
            continue
        edit = project.pole_edits.get(source_pole.id)
        fixture = edit.fixture_type if edit and edit.fixture_type else project.defaults.fixture_type
        if edit and edit.display_name is not None:
            name = placemark.find("k:name", NS)
            if name is None:
                name = ET.SubElement(placemark, f"{{{KML_NS}}}name")
            name.text = edit.display_name
        if edit and edit.location_edit_authorized and edit.longitude is not None and edit.latitude is not None:
            coordinate = placemark.find("k:Point/k:coordinates", NS)
            if coordinate is None:
                raise KmlImportError(f"Source pole {source_pole.id} lost its Point coordinate")
            altitude = source_pole.altitude_m if source_pole.altitude_m is not None else 0
            coordinate.text = f"{edit.longitude:.12g},{edit.latitude:.12g},{altitude:.12g}"
            _set_extended_value(placemark, "lcwa_location_modified", "true")
            _set_extended_value(placemark, "lcwa_source_coordinates", source_pole.raw_coordinates)
        if edit and edit.active is False:
            visibility = placemark.find("k:visibility", NS)
            if visibility is None:
                visibility = ET.SubElement(placemark, f"{{{KML_NS}}}visibility")
            visibility.text = "0"
        style_url = placemark.find("k:styleUrl", NS)
        if style_url is None:
            style_url = ET.SubElement(placemark, f"{{{KML_NS}}}styleUrl")
        style_url.text = f"#lcwa-{fixture.value.lower()}"
        _set_extended_value(placemark, "lcwa_source_pole_id", source_pole.id)
        _set_extended_value(placemark, "lcwa_source_style_url", source_pole.source_style_url or "")
        _set_extended_value(placemark, "lcwa_fixture_type", fixture.value)
        _set_extended_value(placemark, "lcwa_active", str(False if edit and edit.active is False else True).lower())
        if edit and edit.height_m is not None:
            _set_extended_value(placemark, "lcwa_pole_height_m", f"{edit.height_m:g}")
        if edit and edit.external_id:
            _set_extended_value(placemark, "lcwa_external_id", edit.external_id)
        if edit and edit.engineering_notes:
            _set_extended_value(placemark, "lcwa_engineering_notes", edit.engineering_notes)

    ET.register_namespace("", KML_NS)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
