from __future__ import annotations

import json
from pathlib import Path

from app.main import create_app
from app.models import Project


schema_dir = Path(__file__).resolve().parents[2] / "schemas"
schema_dir.mkdir(parents=True, exist_ok=True)
project_target = schema_dir / "project.schema.json"
api_target = schema_dir / "openapi.json"
project_target.write_text(json.dumps(Project.model_json_schema(), indent=2) + "\n", encoding="utf-8")
api_target.write_text(json.dumps(create_app().openapi(), indent=2) + "\n", encoding="utf-8")
print(project_target)
print(api_target)
