from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


ALLOWED_BROWSER_ORIGINS = (
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3070",
)


@pytest.mark.parametrize("origin", ALLOWED_BROWSER_ORIGINS)
def test_local_browser_origins_can_preflight_and_call_api(origin: str) -> None:
    client = TestClient(create_app())

    preflight = client.options(
        "/api/projects/import",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-filename",
        },
    )
    api_response = client.get("/api/health", headers={"Origin": origin})

    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == origin
    assert "POST" in preflight.headers["access-control-allow-methods"]
    assert api_response.status_code == 200
    assert api_response.headers["access-control-allow-origin"] == origin


def test_unrelated_local_origin_cannot_preflight_or_read_api() -> None:
    client = TestClient(create_app())
    origin = "http://127.0.0.1:3071"

    preflight = client.options(
        "/api/projects/import",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-filename",
        },
    )
    api_response = client.get("/api/health", headers={"Origin": origin})

    assert preflight.status_code == 400
    assert "access-control-allow-origin" not in preflight.headers
    assert api_response.status_code == 200
    assert "access-control-allow-origin" not in api_response.headers
