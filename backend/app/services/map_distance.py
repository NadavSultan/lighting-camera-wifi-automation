from __future__ import annotations

import math
from typing import Annotated

from pydantic import Field
from pyproj.exceptions import ProjError

from app.crs import project_transformers, validate_projected_metre_crs
from app.models import StrictModel

Longitude = Annotated[float, Field(ge=-180, le=180, allow_inf_nan=False)]
Latitude = Annotated[float, Field(ge=-90, le=90, allow_inf_nan=False)]


class MapDistanceRequest(StrictModel):
    projected_crs: str = Field(min_length=1, max_length=256)
    start_wgs84: tuple[Longitude, Latitude]
    end_wgs84: tuple[Longitude, Latitude]


class MapDistanceResponse(StrictModel):
    projected_crs: str
    distance_m: float = Field(ge=0, allow_inf_nan=False)


def measure_map_distance(request: MapDistanceRequest) -> MapDistanceResponse:
    """Measure a planar straight line without reading or writing stored data."""
    crs = validate_projected_metre_crs(request.projected_crs)
    to_projected, _ = project_transformers(crs)
    try:
        start = to_projected.transform(*request.start_wgs84, errcheck=True)
        end = to_projected.transform(*request.end_wgs84, errcheck=True)
    except ProjError as exc:
        raise ValueError("Could not transform measurement coordinates to the project CRS") from exc
    if not all(math.isfinite(value) for value in (*start, *end)):
        raise ValueError("Measurement coordinates produced a non-finite projected position")
    distance = math.hypot(end[0] - start[0], end[1] - start[1])
    if not math.isfinite(distance):
        raise ValueError("Measurement distance is not finite")
    return MapDistanceResponse(projected_crs=crs.to_string(), distance_m=distance)
