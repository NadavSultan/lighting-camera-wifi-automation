from __future__ import annotations

import json
from pathlib import Path

from app.main import create_app
from app.models import Project
from app.catalog_models import CameraEquipmentCatalog, FixtureModelCatalog, IesLibrary


schema_dir = Path(__file__).resolve().parents[2] / "schemas"
schema_dir.mkdir(parents=True, exist_ok=True)
project_target = schema_dir / "project.schema.json"
api_target = schema_dir / "openapi.json"
fixture_target = schema_dir / "fixture-model-catalog.schema.json"
ies_target = schema_dir / "ies-library.schema.json"
camera_target = schema_dir / "camera-equipment-catalog.schema.json"
project_target.write_text(json.dumps(Project.model_json_schema(), indent=2) + "\n", encoding="utf-8")
api_target.write_text(json.dumps(create_app().openapi(), indent=2) + "\n", encoding="utf-8")
fixture_target.write_text(json.dumps(FixtureModelCatalog.model_json_schema(), indent=2) + "\n", encoding="utf-8")
ies_target.write_text(json.dumps(IesLibrary.model_json_schema(), indent=2) + "\n", encoding="utf-8")
camera_target.write_text(json.dumps(CameraEquipmentCatalog.model_json_schema(), indent=2) + "\n", encoding="utf-8")
print(project_target)
print(api_target)
print(fixture_target)
print(ies_target)
print(camera_target)
