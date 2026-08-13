from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]

CATALOG_SCHEMAS = {
    "data/fixtures/fixture-types.json": "schemas/fixture-types.schema.json",
    "data/cameras/camera-catalog.json": "schemas/camera-catalog.schema.json",
    "data/luminaires/luminaire-catalog.json": "schemas/luminaire-catalog.schema.json",
    "data/luminaires/ies-inventory.json": "schemas/ies-inventory.schema.json",
    "data/network/cap-constraints.json": "schemas/cap-constraints.schema.json",
    "data/network/wifi-defaults.json": "schemas/wifi-defaults.schema.json",
    "data/standards/calculation-area-types.json": "schemas/calculation-area-types.schema.json",
}

SOURCE_HASHES = {
    "Input/Miracle_Mile_Lighting_Poles.kml": "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328",
    "Input/CAP/CAP datasheet.pdf": "2a1692daef1f3e0537c9c84b144a5063e2041add1e970bbf27a25dad1bb52bce",
    "Input/Camera/VideoCAD Camera Models - Juganu.Xlsx": "7f5e3858b237c353a184edd3324fffa9a1571adb0b94174d48f28a1868b5dd72",
    "Input/Lighting/JLED-SL-120W-PHOENIX1-40-D01.IES": "eb05f9cc5064ab6a0fa19e2886ff0af9cecfa06a7f2ef0bc2e269e57929173c1",
    "Input/Lighting/JLED-SL-100W-PHOENIX1-40-D01.ies": "4a897fb04b6d8f6c75c94a3ceba473391021aee6d506f05357f48bc01d26d363",
    "Input/Lighting/JLED-GL-050W-SOLITAIRE 3B-D02.ies": "4efa14cfe43e2214080bcd09d6424b353322010c07717106bc3218297839c86a",
    "Input/Lighting/JLED-GL-050W-SOLITAIRE 3B-D01.IES": "fda02adb7ca11c6ca5af8e930bdc5e1b8ffb5f558eb8a432a7d4fae87e18db38",
}

APPROVED_UNITS = {
    None,
    "%RH",
    "A",
    "K",
    "MHz",
    "MP",
    "V",
    "VAC/Hz",
    "VDC/A",
    "W",
    "angle",
    "camera",
    "dBm",
    "deg",
    "degC",
    "deg_from_horizontal_down",
    "hop",
    "kbps",
    "km",
    "lamp",
    "lm",
    "lm/lamp",
    "lx",
    "m",
    "mm",
    "ms/hop",
    "multiplier",
    "node",
    "point",
    "px",
    "ratio",
}


class ValidationFailure(Exception):
    pass


def load_json(relative_path: str) -> Any:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def walk(value: Any, path: str = "$"):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def validate_schemas(catalogs: dict[str, Any]) -> None:
    for catalog_path, schema_path in CATALOG_SCHEMAS.items():
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(catalogs[catalog_path]),
            key=lambda error: list(error.absolute_path),
        )
        if errors:
            details = "; ".join(
                f"{catalog_path}:{'/'.join(map(str, error.absolute_path))}: {error.message}"
                for error in errors
            )
            raise ValidationFailure(details)


def validate_traceability(catalogs: dict[str, Any]) -> None:
    for catalog_path, catalog in catalogs.items():
        for object_path, value in walk(catalog):
            if not isinstance(value, dict) or not {"value", "status", "source"}.issubset(value):
                continue
            status = value["status"]
            source = value["source"]
            if value["value"] is None:
                check(status == "unknown", f"{catalog_path}:{object_path}: null value must be unknown")
            else:
                check(status != "unknown", f"{catalog_path}:{object_path}: non-null value cannot be unknown")
            check(value.get("unit") in APPROVED_UNITS, f"{catalog_path}:{object_path}: unapproved unit {value.get('unit')!r}")
            source_file = source.get("file")
            if source_file is not None:
                check((ROOT / source_file).is_file(), f"{catalog_path}:{object_path}: missing source file {source_file}")
            if status == "manufacturer_specification":
                check(source_file is not None, f"{catalog_path}:{object_path}: manufacturer value lacks source file")
            if status == "company_provided_requirement":
                check(bool(source.get("section")), f"{catalog_path}:{object_path}: company requirement lacks source section")
            if status in {"derived_value", "engineering_assumption"}:
                check(bool(value.get("notes")), f"{catalog_path}:{object_path}: {status} lacks explanatory notes")


def ensure_unique(items: list[dict[str, Any]], label: str) -> set[str]:
    identifiers = [item["id"] for item in items]
    check(len(identifiers) == len(set(identifiers)), f"Duplicate identifiers in {label}")
    return set(identifiers)


def validate_fixture_and_wifi(catalogs: dict[str, Any]) -> None:
    fixture_types = catalogs["data/fixtures/fixture-types.json"]["fixture_types"]
    ensure_unique(fixture_types, "fixture types")
    fixtures = {item["id"]: item for item in fixture_types}
    check(set(fixtures) == {"LITE", "WIFI", "SMART"}, "Fixture types must be exactly LITE/WIFI/SMART")
    expected = {
        "LITE": (True, False, False, 0),
        "WIFI": (True, True, False, 0),
        "SMART": (True, True, True, 1),
    }
    for fixture_id, values in expected.items():
        record = fixtures[fixture_id]
        actual = (
            record["provides_lighting"]["value"],
            record["provides_wifi"]["value"],
            record["integrated_cameras"]["value"],
            record["camera_quantity_min"]["value"],
        )
        check(actual == values, f"Inconsistent capabilities for {fixture_id}: {actual}")
    wifi = catalogs["data/network/wifi-defaults.json"]
    check(wifi["coverage_radius"]["value"] > 0, "Wi-Fi radius must be positive")
    for fixture_id in fixtures:
        check(
            wifi["fixture_applicability"][fixture_id]["value"] == fixtures[fixture_id]["provides_wifi"]["value"],
            f"Wi-Fi applicability conflicts with {fixture_id} capability",
        )


def validate_camera(catalogs: dict[str, Any]) -> None:
    catalog = catalogs["data/cameras/camera-catalog.json"]
    camera_ids = ensure_unique(catalog["camera_models"], "camera models")
    lens_ids = ensure_unique(catalog["lenses"], "lenses")
    for camera in catalog["camera_models"]:
        check(camera["resolution_width"]["value"] > 0, f"{camera['id']} resolution width must be positive")
        check(camera["resolution_height"]["value"] > 0, f"{camera['id']} resolution height must be positive")
        check(set(camera["lens_ids"]).issubset(lens_ids), f"{camera['id']} references an unknown lens")
    for lens in catalog["lenses"]:
        check(lens["camera_id"] in camera_ids, f"{lens['id']} references an unknown camera")
        for field in ("horizontal_fov", "vertical_fov"):
            angle = lens[field]["value"]
            if angle is not None:
                check(0 < angle <= 180, f"{lens['id']} {field} outside (0, 180]")
        for candidate in lens["horizontal_fov_candidates"]:
            check(0 < candidate["value"] <= 180, f"{lens['id']} candidate FOV outside (0, 180]")
    integration = catalog["smart_fixture_integration"]
    minimum = integration["allowed_downward_angle_min"]["value"]
    default = integration["default_downward_angle"]["value"]
    maximum = integration["allowed_downward_angle_max"]["value"]
    check(0 <= minimum <= default <= maximum <= 90, "Camera downward-angle convention is inconsistent")


def parse_ies(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    check(bool(lines), f"Empty IES file: {path}")
    tilt_index = next((index for index, line in enumerate(lines) if line.upper().startswith("TILT=")), None)
    check(tilt_index is not None, f"Missing TILT line: {path}")
    keywords: dict[str, str] = {}
    for line in lines[1:tilt_index]:
        match = re.match(r"\[([^]]+)]\s*(.*)", line.strip())
        if match:
            keywords[match.group(1).upper()] = match.group(2).strip()
    numbers: list[float] = []
    for line in lines[tilt_index + 1 :]:
        numbers.extend(float(token) for token in line.split())
    check(len(numbers) >= 13, f"Incomplete numeric header: {path}")
    lamps, lumens, multiplier, vertical_count, horizontal_count, photo_type, units_type, width, length, height = numbers[:10]
    ballast, future, watts = numbers[10:13]
    vertical_count_i, horizontal_count_i = int(vertical_count), int(horizontal_count)
    index = 13
    vertical_angles = numbers[index : index + vertical_count_i]
    index += vertical_count_i
    horizontal_angles = numbers[index : index + horizontal_count_i]
    index += horizontal_count_i
    candela = numbers[index:]
    check(len(vertical_angles) == vertical_count_i, f"Vertical-angle count mismatch: {path}")
    check(len(horizontal_angles) == horizontal_count_i, f"Horizontal-angle count mismatch: {path}")
    check(len(candela) == vertical_count_i * horizontal_count_i, f"Candela count mismatch: {path}")
    return {
        "standard": lines[0].strip(), "tilt": lines[tilt_index].split("=", 1)[1].strip(), "keywords": keywords,
        "lamps": int(lamps), "lumens": lumens, "multiplier": multiplier,
        "vertical_count": vertical_count_i, "horizontal_count": horizontal_count_i,
        "photo_type": int(photo_type), "units_type": int(units_type),
        "width": width, "length": length, "height": height,
        "ballast": ballast, "future": future, "watts": watts,
        "vertical_range": [vertical_angles[0], vertical_angles[-1]],
        "horizontal_range": [horizontal_angles[0], horizontal_angles[-1]],
    }


def validate_ies_and_luminaires(catalogs: dict[str, Any]) -> None:
    luminaires = catalogs["data/luminaires/luminaire-catalog.json"]["luminaires"]
    luminaire_ids = ensure_unique(luminaires, "luminaires")
    inventory = catalogs["data/luminaires/ies-inventory.json"]["ies_files"]
    ensure_unique(inventory, "IES inventory")
    inventory_by_filename = {item["filename"]: item for item in inventory}
    check(len(inventory_by_filename) == len(inventory), "Duplicate IES filenames in inventory")
    actual_ies_files = {path.name for path in (ROOT / "Input/Lighting").iterdir() if path.suffix.lower() == ".ies"}
    check(set(inventory_by_filename) == actual_ies_files, "IES inventory does not exactly match Input/Lighting")
    type_names = {1: "C", 2: "B", 3: "A"}
    unit_names = {1: "ft", 2: "m"}
    for filename, item in inventory_by_filename.items():
        path = ROOT / "Input/Lighting" / filename
        check(path.is_file(), f"Referenced IES file is missing: {filename}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        check(digest == item["file_hash_sha256"], f"IES hash mismatch: {filename}")
        parsed = parse_ies(path)
        comparisons = {
            "ies_standard_version": parsed["standard"], "tilt": parsed["tilt"],
            "number_of_lamps": parsed["lamps"], "lumens_per_lamp": parsed["lumens"],
            "candela_multiplier": parsed["multiplier"], "vertical_angle_count": parsed["vertical_count"],
            "horizontal_angle_count": parsed["horizontal_count"], "vertical_angle_range": parsed["vertical_range"],
            "horizontal_angle_range": parsed["horizontal_range"], "photometric_type": type_names[parsed["photo_type"]],
            "units_type": unit_names[parsed["units_type"]], "ballast_factor": parsed["ballast"],
            "future_use_factor": parsed["future"], "input_watts": parsed["watts"],
        }
        for field, parsed_value in comparisons.items():
            check(item[field]["value"] == parsed_value, f"{filename}: catalog {field} differs from IES")
        for field in ("width", "length", "height"):
            check(item["dimensions"][field]["value"] == parsed[field], f"{filename}: dimension {field} differs")
        check(item["manufacturer"]["value"] == parsed["keywords"].get("MANUFAC"), f"{filename}: manufacturer differs")
        check(item["luminaire_catalog_number"]["value"] == parsed["keywords"].get("LUMINAIRE"), f"{filename}: luminaire identifier differs")
        check(item["associated_luminaire_id"] in luminaire_ids, f"{filename}: unknown associated luminaire")
        check(not item["parse_errors"], f"{filename}: inventory contains parse errors")
    for luminaire in luminaires:
        filename = luminaire["photometric_file"]["value"]
        check(filename in inventory_by_filename, f"{luminaire['id']} references unknown IES file")
        check(inventory_by_filename[filename]["associated_luminaire_id"] == luminaire["id"], f"{luminaire['id']} IES association is not reciprocal")


def validate_cap(catalogs: dict[str, Any]) -> None:
    groups = catalogs["data/network/cap-constraints.json"]["constraints"]
    expected_status = {
        "manufacturer_specifications": "manufacturer_specification",
        "company_provided_requirements": "company_provided_requirement",
        "derived_values": "derived_value",
        "engineering_assumptions": "engineering_assumption",
        "missing_information": "unknown",
    }
    all_constraints: list[dict[str, Any]] = []
    for group, status in expected_status.items():
        for constraint in groups[group]:
            check(constraint["status"] == status, f"CAP constraint {constraint['id']} is in the wrong status group")
            if group == "missing_information":
                check(constraint["value"] is None, f"Missing CAP constraint {constraint['id']} must be null")
            all_constraints.append(constraint)
    ensure_unique(all_constraints, "CAP constraints")
    check(not groups["engineering_assumptions"], "No CAP engineering assumptions are authorized")


def validate_calculation_areas(catalogs: dict[str, Any]) -> None:
    catalog = catalogs["data/standards/calculation-area-types.json"]
    ensure_unique(catalog["area_types"], "calculation area types")
    ensure_unique(catalog["statistics"], "calculation statistics")
    check({item["id"] for item in catalog["area_types"]} == {"road", "sidewalk", "parking", "other"}, "Calculation area types are incomplete")
    for key in ("grid_spacing_x", "grid_spacing_y"):
        check(catalog["defaults"][key]["value"] > 0, f"{key} must be positive")


def validate_source_integrity() -> None:
    for relative_path, expected_hash in SOURCE_HASHES.items():
        path = ROOT / relative_path
        check(path.is_file(), f"Missing supplied source file: {relative_path}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        check(actual_hash == expected_hash, f"Supplied source file changed: {relative_path}")


def main() -> int:
    try:
        catalogs = {path: load_json(path) for path in CATALOG_SCHEMAS}
        validate_schemas(catalogs)
        validate_traceability(catalogs)
        validate_fixture_and_wifi(catalogs)
        validate_camera(catalogs)
        validate_ies_and_luminaires(catalogs)
        validate_cap(catalogs)
        validate_calculation_areas(catalogs)
        validate_source_integrity()
    except (ValidationFailure, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Engineering data validation FAILED: {error}", file=sys.stderr)
        return 1
    print(
        "Engineering data validation PASSED: 7 catalogs matched schemas; identifiers, traceability, "
        "units, camera angles/resolution, fixture capabilities, IES parses/references/hashes, CAP unknowns, "
        "calculation areas, and all supplied-source hashes are valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
