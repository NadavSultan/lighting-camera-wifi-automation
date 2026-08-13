from __future__ import annotations

from pathlib import Path

from fastapi import Body, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.models import HealthResponse, Project, ProjectSummary
from app.services.kml import KmlImportError, MAX_UPLOAD_BYTES, export_updated_kml, import_project, validate_embedded_source
from app.services.store import ProjectNotFoundError, ProjectStore


def create_app(store: ProjectStore | None = None) -> FastAPI:
    project_store = store or ProjectStore()
    app = FastAPI(
        title="Lighting Camera WiFi Automation API",
        version="0.1.0",
        description="Phase 1 local project and KML/KMZ workflow. Existing-pole mode only.",
    )
    app.state.project_store = project_store
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    @app.post("/api/projects", response_model=Project, status_code=201)
    def create_project(name: str = Body(default="Untitled lighting project", embed=True)) -> Project:
        return project_store.save(Project(name=name.strip() or "Untitled lighting project"))

    @app.get("/api/projects", response_model=list[ProjectSummary])
    def list_projects() -> list[ProjectSummary]:
        return project_store.list()

    @app.get("/api/projects/{project_id}", response_model=Project)
    def get_project(project_id: str) -> Project:
        try:
            return project_store.load(project_id)
        except (ProjectNotFoundError, ValueError):
            raise HTTPException(status_code=404, detail="Project not found") from None

    @app.post("/api/projects/import", response_model=Project, status_code=201)
    def import_kml_or_kmz(
        payload: bytes = Body(media_type="application/octet-stream", max_length=MAX_UPLOAD_BYTES),
        x_filename: str = Header(..., alias="X-Filename"),
        x_project_name: str | None = Header(default=None, alias="X-Project-Name"),
    ) -> Project:
        try:
            project = import_project(x_filename, payload, x_project_name)
            return project_store.save(project)
        except (KmlImportError, ValidationError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.put("/api/projects/{project_id}", response_model=Project)
    def save_project(project_id: str, project: Project) -> Project:
        if project.id != project_id:
            raise HTTPException(status_code=409, detail="Project ID does not match request path")
        try:
            return project_store.save(project)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/projects/open", response_model=Project)
    def open_project(project: Project) -> Project:
        try:
            validate_embedded_source(project)
            return project_store.save(project)
        except (KmlImportError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/projects/{project_id}/export/kml")
    def export_kml(project_id: str) -> Response:
        try:
            project = project_store.load(project_id)
            content = export_updated_kml(project)
        except ProjectNotFoundError:
            raise HTTPException(status_code=404, detail="Project not found") from None
        except (KmlImportError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        filename = f"{Path(project.source.file.filename).stem if project.source.file else project.name}-updated.kml"
        return Response(
            content=content,
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    return app


app = create_app()
