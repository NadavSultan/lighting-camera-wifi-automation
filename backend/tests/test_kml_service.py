from __future__ import annotations

import io
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from app.models import FixtureType, PoleEdit
from app.services.kml import KML_NS, KmlImportError, export_updated_kml, import_project


SIMPLE_KML = b"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Test Site</name>
    <Style id="customer"><IconStyle><color>ff123456</color></IconStyle></Style>
    <Folder><name>Existing Poles</name>
      <Placemark id="customer-1">
        <name>Pole A</name><styleUrl>#customer</styleUrl>
        <description>Original description</description>
        <ExtendedData><Data name="asset"><value>A-101</value></Data></ExtendedData>
        <Point><coordinates>-80.1,25.7,3.25</coordinates></Point>
      </Placemark>
      <Placemark><name>Pole B</name><Point><coordinates>-80.100002,25.7,0</coordinates></Point></Placemark>
    </Folder>
    <Placemark><name>Road</name><LineString><coordinates>-80.1,25.7 -80.2,25.8</coordinates></LineString></Placemark>
  </Document>
</kml>"""


def test_import_preserves_customer_values_and_separates_warnings() -> None:
    project = import_project("customer.kml", SIMPLE_KML)

    assert project.mode.value == "existing-poles"
    assert project.proposed_layout_authorized is False
    assert project.source.document_name == "Test Site"
    assert len(project.source.poles) == 2
    assert project.source.unsupported_geometry_count == 1
    pole = project.source.poles[0]
    assert pole.id == "customer-1"
    assert pole.folder_path == ["Existing Poles"]
    assert pole.description == "Original description"
    assert pole.extended_data == {"asset": "A-101"}
    assert pole.source_style_url == "#customer"
    assert pole.source_style_color == "ff123456"
    assert pole.raw_coordinates == "-80.1,25.7,3.25"
    assert project.projected_crs == "EPSG:32617"
    assert any(warning.code == "unsupported_geometry" for warning in project.warnings)
    assert any(warning.code == "near_duplicate_coordinate" for warning in project.warnings)


def test_kmz_import_uses_doc_kml_and_preserves_exact_upload() -> None:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("doc.kml", SIMPLE_KML)
        archive.writestr("images/icon.txt", "reference")
    content = stream.getvalue()

    project = import_project("customer.kmz", content)

    assert project.source.file is not None
    assert project.source.file.kml_entry == "doc.kml"
    assert project.source.file.size_bytes == len(content)
    assert len(project.source.poles) == 2


def test_kmz_rejects_unsafe_path() -> None:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("../doc.kml", SIMPLE_KML)

    with pytest.raises(KmlImportError, match="unsafe archive path"):
        import_project("unsafe.kmz", stream.getvalue())


def test_malformed_point_is_warned_without_correction() -> None:
    malformed = SIMPLE_KML.replace(b"-80.1,25.7,3.25", b"999,25.7,3.25")

    project = import_project("malformed.kml", malformed)

    assert len(project.source.poles) == 1
    warning = next(w for w in project.warnings if w.code == "malformed_coordinate")
    assert warning.severity.value == "error"
    assert warning.details["raw_coordinates"] == "999,25.7,3.25"


def test_export_applies_edits_but_preserves_source_model() -> None:
    project = import_project("customer.kml", SIMPLE_KML)
    source = project.source.poles[0]
    project.pole_edits[source.id] = PoleEdit(
        pole_id=source.id,
        display_name="Pole A - SMART",
        external_id="ENG-001",
        fixture_type=FixtureType.SMART,
        height_m=8.5,
        active=False,
        engineering_notes="Field verified",
    )

    exported = export_updated_kml(project)
    root = ET.fromstring(exported)
    ns = {"k": KML_NS}
    placemark = root.find(".//k:Placemark[@id='customer-1']", ns)
    assert placemark is not None
    assert placemark.findtext("k:name", namespaces=ns) == "Pole A - SMART"
    assert placemark.findtext("k:Point/k:coordinates", namespaces=ns) == "-80.1,25.7,3.25"
    assert placemark.findtext("k:styleUrl", namespaces=ns) == "#lcwa-smart"
    assert placemark.findtext("k:visibility", namespaces=ns) == "0"
    data = {
        element.get("name"): element.findtext("k:value", namespaces=ns)
        for element in placemark.findall("k:ExtendedData/k:Data", ns)
    }
    assert data["asset"] == "A-101"
    assert data["lcwa_fixture_type"] == "SMART"
    assert data["lcwa_pole_height_m"] == "8.5"
    assert source.name == "Pole A"
    assert source.raw_coordinates == "-80.1,25.7,3.25"


def test_sample_customer_file_inventory() -> None:
    source = Path(__file__).resolve().parents[2] / "Input" / "Miracle_Mile_Lighting_Poles.kml"
    project = import_project(source.name, source.read_bytes())

    assert len(project.source.poles) == 74
    assert project.source.unsupported_geometry_count == 0
    assert project.projected_crs == "EPSG:32617"
    assert {tuple(pole.folder_path) for pole in project.source.poles} == {
        ("Cobra Head (40)",),
        ("Other (14)",),
        ("Decorative (10)",),
        ("Lighting and Camera (8)",),
        ("Environmental, Lighting and Camera (2)",),
    }
