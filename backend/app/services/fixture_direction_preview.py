from __future__ import annotations

import math

from pydantic import Field
from pyproj.exceptions import ProjError

from app.catalog_models import FixtureModelCatalog
from app.crs import project_transformers, validate_projected_metre_crs
from app.models import Project, StrictModel


class FixtureDirection(StrictModel):
    pole_id: str
    origin_wgs84: tuple[float, float]
    endpoint_wgs84: tuple[float, float]
    fixture_azimuth_deg: float
    active: bool


class FixtureDirectionUnavailable(StrictModel):
    pole_id: str
    reason: str


class FixtureDirectionPreviewResponse(StrictModel):
    directions: list[FixtureDirection] = Field(default_factory=list)
    unavailable: list[FixtureDirectionUnavailable] = Field(default_factory=list)


def projected_direction_endpoint(
    x: float,
    y: float,
    azimuth_deg: float,
    length_m: float = 1.0,
) -> tuple[float, float]:
    """Return a one-metre (by default) grid-north-clockwise direction sample in projected metres."""
    if not all(math.isfinite(value) for value in (x, y, azimuth_deg, length_m)):
        raise ValueError("projected direction inputs must be finite")
    angle = math.radians(azimuth_deg)
    return (x + length_m * math.sin(angle), y + length_m * math.cos(angle))


def preview_fixture_directions(
    project: Project,
    fixtures: FixtureModelCatalog,
) -> FixtureDirectionPreviewResponse:
    """Build read-only WGS84 direction segments for configured lighting fixtures.

    Does not save the project, mutate catalogs, or run lighting calculations.
    """
    directions: list[FixtureDirection] = []
    unavailable: list[FixtureDirectionUnavailable] = []

    fixture_revisions = {
        (item.id, item.revision): item
        for item in [*fixtures.fixture_models, *fixtures.fixture_model_history]
    }
    fixture_current = {item.id: item for item in fixtures.fixture_models}

    crs_error: str | None = None
    to_projected = None
    to_wgs84 = None
    if not project.projected_crs:
        crs_error = "A project-selected projected CRS is required for fixture-direction preview"
    else:
        try:
            crs = validate_projected_metre_crs(project.projected_crs)
            to_projected, to_wgs84 = project_transformers(crs)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

    for pole in project.source.poles:
        edit = project.pole_edits.get(pole.id)
        config = edit.fixture_configuration if edit is not None else None
        if config is None:
            unavailable.append(
                FixtureDirectionUnavailable(
                    pole_id=pole.id,
                    reason="fixture configuration is missing",
                )
            )
            continue

        model = fixture_revisions.get((config.fixture_model_id, config.fixture_model_revision))
        current_model = fixture_current.get(config.fixture_model_id)
        if model is None or current_model is None or not current_model.active:
            unavailable.append(
                FixtureDirectionUnavailable(
                    pole_id=pole.id,
                    reason="fixture model/revision is missing or inactive",
                )
            )
            continue
        if not model.capabilities.lighting:
            unavailable.append(
                FixtureDirectionUnavailable(
                    pole_id=pole.id,
                    reason="fixture model is not lighting-capable",
                )
            )
            continue

        if crs_error is not None or to_projected is None or to_wgs84 is None:
            unavailable.append(
                FixtureDirectionUnavailable(pole_id=pole.id, reason=crs_error or "projected CRS is unavailable")
            )
            continue

        try:
            origin_x, origin_y = to_projected.transform(pole.longitude, pole.latitude)
            if not (math.isfinite(origin_x) and math.isfinite(origin_y)):
                raise ValueError("non-finite projected origin")
            end_x, end_y = projected_direction_endpoint(
                origin_x, origin_y, config.fixture_azimuth_deg, length_m=1.0
            )
            origin_lon, origin_lat = to_wgs84.transform(origin_x, origin_y)
            end_lon, end_lat = to_wgs84.transform(end_x, end_y)
            if not all(math.isfinite(value) for value in (origin_lon, origin_lat, end_lon, end_lat)):
                raise ValueError("non-finite WGS84 direction endpoints")
        except (ValueError, ProjError) as exc:
            unavailable.append(
                FixtureDirectionUnavailable(
                    pole_id=pole.id,
                    reason=f"direction preview could not be projected: {exc}",
                )
            )
            continue

        active = True if edit.active is None else bool(edit.active)
        directions.append(
            FixtureDirection(
                pole_id=pole.id,
                origin_wgs84=(origin_lon, origin_lat),
                endpoint_wgs84=(end_lon, end_lat),
                fixture_azimuth_deg=config.fixture_azimuth_deg,
                active=active,
            )
        )

    return FixtureDirectionPreviewResponse(directions=directions, unavailable=unavailable)
