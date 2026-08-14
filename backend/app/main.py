from __future__ import annotations

from pathlib import Path

from fastapi import Body, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.catalog_models import (
    CameraEquipmentCatalog,
    CameraModel,
    CameraMountingTemplateRevision,
    FixtureModel,
    FixtureModelCatalog,
    IesFixtureAssociation,
    IesFileRecord,
    IesLibrary,
    LensConfiguration,
)
from app.models import HealthResponse, Project, ProjectSummary, migrate_project_payload
from app.services.catalogs import CatalogNotFoundError, CatalogStore
from app.services.configuration import (
    BulkPoleConfigurationRequest,
    apply_bulk_configuration,
    validate_project_configuration,
)
from app.services.ies import IesValidationError, parse_ies_upload
from app.services.kml import KmlImportError, MAX_UPLOAD_BYTES, export_updated_kml, import_project, validate_embedded_source
from app.services.store import ProjectNotFoundError, ProjectStore


def create_app(store: ProjectStore | None = None, catalog_store: CatalogStore | None = None) -> FastAPI:
    project_store = store or ProjectStore()
    catalogs = catalog_store or CatalogStore()
    app = FastAPI(
        title="Lighting Camera WiFi Automation API",
        version="0.2.0",
        description="Phase 2 local fixture, IES, camera, and existing-pole configuration workflow.",
    )
    app.state.project_store = project_store
    app.state.catalog_store = catalogs
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
            errors = validate_project_configuration(project, catalogs.fixtures(), catalogs.cameras(), catalogs.ies())
            if errors:
                raise ValueError("; ".join(errors))
            return project_store.save(project)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/projects/open", response_model=Project)
    def open_project(payload: dict = Body(...)) -> Project:
        try:
            project = Project.model_validate(migrate_project_payload(payload))
            validate_embedded_source(project)
            errors = validate_project_configuration(project, catalogs.fixtures(), catalogs.cameras(), catalogs.ies())
            if errors:
                raise ValueError("; ".join(errors))
            return project_store.save(project)
        except (KmlImportError, ValidationError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.patch("/api/projects/{project_id}/poles/bulk", response_model=Project)
    def bulk_configure_poles(project_id: str, request: BulkPoleConfigurationRequest) -> Project:
        try:
            project = project_store.load(project_id)
            updated = apply_bulk_configuration(project, request, catalogs.fixtures())
            errors = validate_project_configuration(updated, catalogs.fixtures(), catalogs.cameras(), catalogs.ies())
            if errors:
                raise ValueError("; ".join(errors))
            return project_store.save(updated)
        except ProjectNotFoundError:
            raise HTTPException(status_code=404, detail="Project not found") from None
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/catalogs/fixtures", response_model=FixtureModelCatalog)
    def get_fixture_catalog() -> FixtureModelCatalog:
        return catalogs.fixtures()

    @app.put("/api/catalogs/fixtures/{fixture_id}", response_model=FixtureModel)
    def upsert_fixture(fixture_id: str, model: FixtureModel) -> FixtureModel:
        if fixture_id != model.id:
            raise HTTPException(status_code=409, detail="Fixture ID does not match request path")
        try:
            return catalogs.upsert_fixture(model)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/catalogs/fixtures/{fixture_id}/template-revisions", response_model=FixtureModel, status_code=201)
    def add_template_revision(fixture_id: str, revision: CameraMountingTemplateRevision) -> FixtureModel:
        try:
            return catalogs.add_template_revision(fixture_id, revision)
        except CatalogNotFoundError:
            raise HTTPException(status_code=404, detail="Fixture model not found") from None
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/catalogs/cameras", response_model=CameraEquipmentCatalog)
    def get_camera_catalog() -> CameraEquipmentCatalog:
        return catalogs.cameras()

    @app.put("/api/catalogs/cameras/{camera_id}", response_model=CameraModel)
    def upsert_camera(camera_id: str, camera: CameraModel) -> CameraModel:
        if camera_id != camera.id:
            raise HTTPException(status_code=409, detail="Camera ID does not match request path")
        try:
            return catalogs.upsert_camera(camera)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.delete("/api/catalogs/cameras/{camera_id}", status_code=204)
    def delete_camera(camera_id: str) -> Response:
        try:
            catalogs.delete_camera(camera_id)
            return Response(status_code=204)
        except CatalogNotFoundError:
            raise HTTPException(status_code=404, detail="Camera model not found") from None
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.put("/api/catalogs/lenses/{lens_id}", response_model=LensConfiguration)
    def upsert_lens(lens_id: str, lens: LensConfiguration) -> LensConfiguration:
        if lens_id != lens.id:
            raise HTTPException(status_code=409, detail="Lens ID does not match request path")
        try:
            return catalogs.upsert_lens(lens)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.delete("/api/catalogs/lenses/{lens_id}", status_code=204)
    def delete_lens(lens_id: str) -> Response:
        try:
            catalogs.delete_lens(lens_id)
            return Response(status_code=204)
        except CatalogNotFoundError:
            raise HTTPException(status_code=404, detail="Lens not found") from None
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/api/catalogs/ies", response_model=IesLibrary)
    def get_ies_library() -> IesLibrary:
        return catalogs.ies()

    @app.post("/api/catalogs/ies/upload", response_model=IesFileRecord, status_code=201)
    def upload_ies(
        payload: bytes = Body(media_type="application/octet-stream", max_length=20 * 1024 * 1024),
        x_filename: str = Header(..., alias="X-Filename"),
    ):
        try:
            return catalogs.add_ies(parse_ies_upload(x_filename, payload))
        except (IesValidationError, ValidationError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.patch("/api/catalogs/ies/{ies_id}", response_model=IesFileRecord)
    def set_ies_active(ies_id: str, active: bool = Body(..., embed=True)) -> IesFileRecord:
        try:
            return catalogs.set_ies_active(ies_id, active)
        except CatalogNotFoundError:
            raise HTTPException(status_code=404, detail="IES file not found") from None

    @app.put("/api/catalogs/ies/{ies_id}/fixtures/{fixture_id}", response_model=IesFixtureAssociation)
    def associate_ies(ies_id: str, fixture_id: str, active: bool = Body(default=True, embed=True)) -> IesFixtureAssociation:
        try:
            return catalogs.associate_ies(IesFixtureAssociation(ies_file_id=ies_id, fixture_model_id=fixture_id, active=active))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.delete("/api/catalogs/ies/{ies_id}/fixtures/{fixture_id}", status_code=204)
    def remove_ies_association(ies_id: str, fixture_id: str) -> Response:
        try:
            catalogs.remove_ies_association(ies_id, fixture_id)
            return Response(status_code=204)
        except CatalogNotFoundError:
            raise HTTPException(status_code=404, detail="IES association not found") from None

    @app.put("/api/catalogs/fixtures/{fixture_id}/default-ies/{ies_id}", response_model=FixtureModel)
    def set_default_ies(fixture_id: str, ies_id: str) -> FixtureModel:
        try:
            return catalogs.set_default_ies(fixture_id, ies_id)
        except CatalogNotFoundError:
            raise HTTPException(status_code=404, detail="Fixture model not found") from None
        except ValueError as exc:
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
