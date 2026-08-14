from __future__ import annotations

import base64
import hashlib
import re
from datetime import datetime, timezone

from app.catalog_models import IesFileRecord, IesParsedMetadata


class IesValidationError(ValueError):
    pass


def parse_ies_upload(filename: str, content: bytes) -> IesFileRecord:
    if not filename.lower().endswith(".ies"):
        raise IesValidationError("Only .ies photometric files are supported")
    if not content or len(content) > 20 * 1024 * 1024:
        raise IesValidationError("IES file must contain between 1 byte and 20 MB")
    try:
        lines = content.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError as exc:
        raise IesValidationError("IES file is not valid UTF-8/ASCII text") from exc
    if not lines or lines[0].strip() not in {"IESNA:LM-63-1995", "IESNA:LM-63-2002"}:
        raise IesValidationError("Unsupported IES format; LM-63-1995 or LM-63-2002 is required")
    tilt_index = next((index for index, line in enumerate(lines) if line.strip().upper().startswith("TILT=")), None)
    if tilt_index is None:
        raise IesValidationError("Missing TILT declaration")
    tilt = lines[tilt_index].split("=", 1)[1].strip().upper()
    if tilt != "NONE":
        raise IesValidationError("Unsupported IES TILT data; Phase 2 accepts TILT=NONE only")
    keywords: dict[str, str] = {}
    for line in lines[1:tilt_index]:
        match = re.match(r"\[([^]]+)]\s*(.*)", line.strip())
        if match:
            keywords[match.group(1).upper()] = match.group(2).strip()
    try:
        numbers = [float(token) for line in lines[tilt_index + 1 :] for token in line.split()]
    except ValueError as exc:
        raise IesValidationError("IES numeric data contains a non-numeric value") from exc
    if len(numbers) < 13:
        raise IesValidationError("Incomplete IES numeric header")
    lamps, _, _, vertical_count, horizontal_count, photometric_type, units_type = numbers[:7]
    watts = numbers[12]
    v_count, h_count = int(vertical_count), int(horizontal_count)
    if v_count <= 0 or h_count <= 0 or vertical_count != v_count or horizontal_count != h_count:
        raise IesValidationError("IES angle counts must be positive integers")
    if int(photometric_type) != 1:
        raise IesValidationError("Unsupported photometric type; Phase 2 accepts Type C only")
    if int(units_type) not in {1, 2}:
        raise IesValidationError("Unsupported IES dimension unit code")
    start = 13
    vertical = numbers[start : start + v_count]
    horizontal = numbers[start + v_count : start + v_count + h_count]
    candela = numbers[start + v_count + h_count :]
    if len(vertical) != v_count or len(horizontal) != h_count:
        raise IesValidationError("IES angle data is incomplete")
    expected_candela = v_count * h_count
    if len(candela) != expected_candela:
        raise IesValidationError(f"IES candela count mismatch: expected {expected_candela}, found {len(candela)}")
    digest = hashlib.sha256(content).hexdigest()
    return IesFileRecord(
        id=f"ies-{digest[:16]}",
        original_filename=filename.split("/")[-1].split("\\")[-1],
        sha256=digest,
        uploaded_at=datetime.now(timezone.utc),
        ies_format_version=lines[0].strip(),
        original_content_base64=base64.b64encode(content).decode("ascii"),
        parsed_metadata=IesParsedMetadata(
            manufacturer=keywords.get("MANUFAC"),
            luminaire_catalog_number=keywords.get("LUMINAIRE"),
            lamp_count=int(lamps),
            input_watts=watts,
            photometric_type="C",
            units="ft" if int(units_type) == 1 else "m",
            vertical_angle_count=v_count,
            horizontal_angle_count=h_count,
            vertical_angle_range_deg=(vertical[0], vertical[-1]),
            horizontal_angle_range_deg=(horizontal[0], horizontal[-1]),
            candela_value_count=len(candela),
        ),
        validation_status="valid",
    )
