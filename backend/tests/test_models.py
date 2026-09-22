from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import HealthResponse, OperatingMode, PoleEdit, Project, SCHEMA_VERSION, SOFTWARE_VERSION


def test_coordinate_edit_requires_explicit_authorization() -> None:
    with pytest.raises(ValidationError, match="location_edit_authorized"):
        PoleEdit(pole_id="pole-1", longitude=-80.1, latitude=25.7)


def test_partial_coordinate_edit_is_rejected() -> None:
    with pytest.raises(ValidationError, match="provided together"):
        PoleEdit(pole_id="pole-1", longitude=-80.1, location_edit_authorized=True)


def test_proposed_layout_requires_explicit_authorization() -> None:
    with pytest.raises(ValidationError, match="explicit authorization"):
        Project(mode=OperatingMode.PROPOSED_LAYOUT)


def test_edits_cannot_reference_unknown_poles() -> None:
    with pytest.raises(ValidationError, match="unknown source poles"):
        Project(pole_edits={"missing": PoleEdit(pole_id="missing")})


def test_bl016_current_versions_and_defaults() -> None:
    project = Project()
    assert SCHEMA_VERSION == "2.8.0"
    assert SOFTWARE_VERSION == "0.8.0"
    assert project.schema_version == "2.8.0"
    assert project.software_version == "0.8.0"
    assert project.camera_pixel_density_profile.lower_projection_height_m == 0.5
    assert project.camera_pixel_density_profile.upper_projection_height_m == 2.0
    assert project.camera_pixel_density_profile.measurement_height_m == 1.25
    assert project.camera_pixel_density.state.status == "not-calculated"
    assert project.camera_pixel_density.result is None
    assert project.layer_state.camera_pixel_density is False
    assert HealthResponse().version == "0.8.0"
