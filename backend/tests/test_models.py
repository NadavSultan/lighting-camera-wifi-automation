from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import OperatingMode, PoleEdit, Project


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
