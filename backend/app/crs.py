from __future__ import annotations

from pyproj import CRS, Transformer
from pyproj.exceptions import CRSError, ProjError


METRE_UNIT_NAMES = {"metre", "meter"}


def validate_projected_metre_crs(value: str) -> CRS:
    """Parse and enforce the engineering CRS contract shared by every project path."""
    try:
        crs = CRS.from_user_input(value)
    except CRSError as exc:
        raise ValueError(f"Invalid project engineering CRS: {value}") from exc
    axes = crs.axis_info[:2]
    if not crs.is_projected or len(axes) < 2 or any(axis.unit_name.lower() not in METRE_UNIT_NAMES for axis in axes):
        raise ValueError(f"Project engineering CRS must be projected and use metre axes: {value}")
    return crs


def project_transformers(crs: CRS) -> tuple[Transformer, Transformer]:
    """Construct the shared WGS84/project transformers with controlled pyproj failures."""
    try:
        return (
            Transformer.from_crs("EPSG:4326", crs, always_xy=True),
            Transformer.from_crs(crs, "EPSG:4326", always_xy=True),
        )
    except (CRSError, ProjError) as exc:
        raise ValueError("Could not construct transformations for the project engineering CRS") from exc
