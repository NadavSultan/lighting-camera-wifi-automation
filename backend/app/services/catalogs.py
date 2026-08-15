from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path

from app.catalog_models import (
    CameraEquipmentCatalog,
    CameraModel,
    CameraMountingTemplateRevision,
    FixtureModel,
    FixtureModelCatalog,
    IesFileRecord,
    IesFixtureAssociation,
    IesLibrary,
    LensConfiguration,
)


class CatalogNotFoundError(KeyError):
    pass


class CatalogStore:
    def __init__(self, root: Path | None = None, seed_root: Path | None = None) -> None:
        configured = os.environ.get("LCWA_CATALOG_DIR")
        self.root = root or (Path(configured) if configured else Path(__file__).resolve().parents[2] / "data" / "catalogs")
        self.seed_root = seed_root or Path(__file__).resolve().parents[3] / "data" / "phase2"

    def fixtures(self) -> FixtureModelCatalog:
        return FixtureModelCatalog.model_validate(self._read("fixture-model-catalog.json"))

    def cameras(self) -> CameraEquipmentCatalog:
        return CameraEquipmentCatalog.model_validate(self._read("camera-equipment-catalog.json"))

    def ies(self) -> IesLibrary:
        return IesLibrary.model_validate(self._read("ies-library.json"))

    def save_fixtures(self, catalog: FixtureModelCatalog) -> FixtureModelCatalog:
        self._write("fixture-model-catalog.json", catalog.model_dump(mode="json"))
        return catalog

    def save_cameras(self, catalog: CameraEquipmentCatalog) -> CameraEquipmentCatalog:
        self._write("camera-equipment-catalog.json", catalog.model_dump(mode="json"))
        return catalog

    def save_ies(self, library: IesLibrary) -> IesLibrary:
        self._write("ies-library.json", library.model_dump(mode="json"))
        return library

    def upsert_fixture(self, model: FixtureModel) -> FixtureModel:
        catalog = self.fixtures()
        index = next((i for i, item in enumerate(catalog.fixture_models) if item.id == model.id), None)
        if index is None:
            if model.revision != 1:
                raise ValueError("new fixture models must start at revision 1")
            catalog.fixture_models.append(model)
        else:
            existing = catalog.fixture_models[index]
            if model.mounting_template_revisions != existing.mounting_template_revisions:
                raise ValueError("mounting templates can change only through an explicit template-revision action")
            model.revision = existing.revision + 1
            catalog.fixture_model_history.append(deepcopy(existing))
            catalog.fixture_models[index] = model
        validated = FixtureModelCatalog.model_validate(catalog.model_dump())
        self.save_fixtures(validated)
        return model

    def add_template_revision(self, fixture_id: str, revision: CameraMountingTemplateRevision) -> FixtureModel:
        catalog = self.fixtures()
        model = next((item for item in catalog.fixture_models if item.id == fixture_id), None)
        if model is None:
            raise CatalogNotFoundError(fixture_id)
        if not model.capabilities.cameras:
            raise ValueError("camera mounting templates are allowed only for SMART fixtures")
        if revision.revision != max(item.revision for item in model.mounting_template_revisions) + 1:
            raise ValueError("template revision must be the next immutable revision")
        catalog.fixture_model_history.append(deepcopy(model))
        model.mounting_template_revisions.append(revision)
        model.current_mounting_template_revision = revision.revision
        model.revision += 1
        self.save_fixtures(FixtureModelCatalog.model_validate(catalog.model_dump()))
        return model

    def upsert_camera(self, camera: CameraModel) -> CameraModel:
        catalog = self.cameras()
        camera.compatible_lens_ids = [lens.id for lens in catalog.lenses if camera.id in lens.compatible_camera_model_ids]
        index = next((i for i, item in enumerate(catalog.camera_models) if item.id == camera.id), None)
        if index is None:
            if camera.revision != 1:
                raise ValueError("new camera models must start at revision 1")
            catalog.camera_models.append(camera)
        else:
            existing = catalog.camera_models[index]
            camera.revision = existing.revision + 1
            catalog.camera_model_history.append(deepcopy(existing))
            catalog.camera_models[index] = camera
        self.save_cameras(CameraEquipmentCatalog.model_validate(catalog.model_dump()))
        return camera

    def delete_camera(self, camera_id: str) -> None:
        catalog = self.cameras()
        if any(camera_id in lens.compatible_camera_model_ids for lens in catalog.lenses):
            raise ValueError("camera is still referenced by a compatible lens; deactivate it or remove associations first")
        remaining = [item for item in catalog.camera_models if item.id != camera_id]
        if len(remaining) == len(catalog.camera_models):
            raise CatalogNotFoundError(camera_id)
        catalog.camera_models = remaining
        self.save_cameras(catalog)

    def upsert_lens(self, lens: LensConfiguration) -> LensConfiguration:
        catalog = self.cameras()
        index = next((i for i, item in enumerate(catalog.lenses) if item.id == lens.id), None)
        if index is None:
            if lens.revision != 1:
                raise ValueError("new lenses must start at revision 1")
            catalog.lenses.append(lens)
        else:
            existing = catalog.lenses[index]
            lens.revision = existing.revision + 1
            catalog.lens_history.append(deepcopy(existing))
            catalog.lenses[index] = lens
        for camera in catalog.camera_models:
            derived = [item.id for item in catalog.lenses if camera.id in item.compatible_camera_model_ids]
            if camera.compatible_lens_ids != derived:
                catalog.camera_model_history.append(deepcopy(camera))
                camera.compatible_lens_ids = derived
                camera.revision += 1
        self.save_cameras(CameraEquipmentCatalog.model_validate(catalog.model_dump()))
        return lens

    def delete_lens(self, lens_id: str) -> None:
        catalog = self.cameras()
        if any(lens_id in camera.compatible_lens_ids for camera in catalog.camera_models):
            raise ValueError("lens is still referenced by a compatible camera; deactivate it or remove associations first")
        remaining = [item for item in catalog.lenses if item.id != lens_id]
        if len(remaining) == len(catalog.lenses):
            raise CatalogNotFoundError(lens_id)
        catalog.lenses = remaining
        self.save_cameras(catalog)

    def add_ies(self, record: IesFileRecord) -> IesFileRecord:
        library = self.ies()
        if any(item.sha256 == record.sha256 for item in library.files):
            return next(item for item in library.files if item.sha256 == record.sha256)
        library.files.append(record)
        self.save_ies(library)
        return record

    def set_ies_active(self, ies_id: str, active: bool) -> IesFileRecord:
        library = self.ies()
        record = next((item for item in library.files if item.id == ies_id), None)
        if record is None:
            raise CatalogNotFoundError(ies_id)
        if active and record.validation_status != "valid":
            raise ValueError("only valid IES files can be activated")
        record.active = active
        record.revision += 1
        if not active:
            for association in library.fixture_associations:
                if association.ies_file_id == ies_id:
                    association.active = False
            fixtures = self.fixtures()
            changed = False
            for model in fixtures.fixture_models:
                if model.default_ies_file_id == ies_id:
                    fixtures.fixture_model_history.append(deepcopy(model))
                    model.default_ies_file_id = None
                    model.revision += 1
                    changed = True
            if changed:
                self.save_fixtures(fixtures)
        self.save_ies(library)
        return record

    def associate_ies(self, association: IesFixtureAssociation) -> IesFixtureAssociation:
        fixture_ids = {item.id for item in self.fixtures().fixture_models}
        if association.fixture_model_id not in fixture_ids:
            raise ValueError("IES association references an unknown fixture model")
        library = self.ies()
        record = next((item for item in library.files if item.id == association.ies_file_id), None)
        if record is None:
            raise ValueError("IES association references an unknown file")
        if association.active and (not record.active or record.validation_status != "valid"):
            raise ValueError("active IES association requires an active valid file")
        existing = next((item for item in library.fixture_associations if (item.ies_file_id, item.fixture_model_id) == (association.ies_file_id, association.fixture_model_id)), None)
        if existing:
            existing.active = association.active
        else:
            library.fixture_associations.append(association)
        self.save_ies(library)
        return association

    def remove_ies_association(self, ies_id: str, fixture_id: str) -> None:
        library = self.ies()
        original = len(library.fixture_associations)
        library.fixture_associations = [item for item in library.fixture_associations if (item.ies_file_id, item.fixture_model_id) != (ies_id, fixture_id)]
        if len(library.fixture_associations) == original:
            raise CatalogNotFoundError(f"{ies_id}/{fixture_id}")
        fixtures = self.fixtures()
        model = next((item for item in fixtures.fixture_models if item.id == fixture_id), None)
        if model and model.default_ies_file_id == ies_id:
            fixtures.fixture_model_history.append(deepcopy(model))
            model.default_ies_file_id = None
            model.compatible_ies_file_ids = [value for value in model.compatible_ies_file_ids if value != ies_id]
            model.revision += 1
            self.save_fixtures(fixtures)
        self.save_ies(library)

    def set_default_ies(self, fixture_id: str, ies_id: str) -> FixtureModel:
        library = self.ies()
        record = next((item for item in library.files if item.id == ies_id), None)
        if record is None or not record.active or record.validation_status != "valid":
            raise ValueError("default IES requires an active valid file")
        if not any(item.active and item.ies_file_id == ies_id and item.fixture_model_id == fixture_id for item in library.fixture_associations):
            raise ValueError("default IES requires an active explicit fixture association")
        catalog = self.fixtures()
        model = next((item for item in catalog.fixture_models if item.id == fixture_id), None)
        if model is None:
            raise CatalogNotFoundError(fixture_id)
        catalog.fixture_model_history.append(deepcopy(model))
        if ies_id not in model.compatible_ies_file_ids:
            model.compatible_ies_file_ids.append(ies_id)
        model.default_ies_file_id = ies_id
        model.revision += 1
        self.save_fixtures(catalog)
        return model

    def _read(self, filename: str) -> dict:
        path = self.root / filename
        source = path if path.exists() else self.seed_root / filename
        payload = json.loads(source.read_text(encoding="utf-8"))
        if payload.get("schema_version") == "1.0.0":
            payload["schema_version"] = "1.1.0"
            if filename == "fixture-model-catalog.json":
                for model in payload.get("fixture_models", []):
                    for template in model.get("mounting_template_revisions", []):
                        for slot in template.get("slots", []):
                            if slot.get("camera_model_id") and slot.get("camera_model_revision") is None:
                                slot["camera_model_revision"] = 1
                            if slot.get("lens_id") and slot.get("lens_revision") is None:
                                slot["lens_revision"] = 1
        return payload

    def _write(self, filename: str, payload: dict) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / filename
        temporary = self.root / f"{filename}.tmp"
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(target)
