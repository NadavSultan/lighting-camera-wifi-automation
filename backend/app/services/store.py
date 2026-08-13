from __future__ import annotations

import base64
import json
import os
from pathlib import Path

from app.models import Project, ProjectSummary, utc_now


class ProjectNotFoundError(FileNotFoundError):
    pass


class ProjectStore:
    def __init__(self, root: Path | None = None) -> None:
        configured = os.environ.get("LCWA_DATA_DIR")
        self.root = root or (Path(configured) if configured else Path(__file__).resolve().parents[2] / "data" / "projects")

    def _directory(self, project_id: str) -> Path:
        if not project_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in project_id):
            raise ValueError("Invalid project ID")
        return self.root / project_id

    def save(self, project: Project) -> Project:
        directory = self._directory(project.id)
        target = directory / "project.json"
        if target.exists():
            existing_project = Project.model_validate_json(target.read_text(encoding="utf-8"))
            if existing_project.source != project.source:
                raise ValueError("Original customer source data is immutable for an existing project")

        source_target: Path | None = None
        source_content: bytes | None = None
        if project.source.file is not None:
            source_target = directory / "sources" / project.source.file.filename
            source_content = base64.b64decode(project.source.file.content_base64, validate=True)
            if source_target.exists() and source_target.read_bytes() != source_content:
                raise ValueError("An immutable source file would be overwritten with different content")

        project.updated_at = utc_now()
        directory.mkdir(parents=True, exist_ok=True)
        if source_target is not None and source_content is not None and not source_target.exists():
            source_target.parent.mkdir(exist_ok=True)
            source_target.write_bytes(source_content)

        target = directory / "project.json"
        temporary = directory / "project.json.tmp"
        temporary.write_text(project.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(target)
        return project

    def load(self, project_id: str) -> Project:
        target = self._directory(project_id) / "project.json"
        if not target.exists():
            raise ProjectNotFoundError(project_id)
        return Project.model_validate_json(target.read_text(encoding="utf-8"))

    def list(self) -> list[ProjectSummary]:
        if not self.root.exists():
            return []
        summaries: list[ProjectSummary] = []
        for path in self.root.glob("*/project.json"):
            try:
                project = Project.model_validate_json(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            summaries.append(ProjectSummary(
                id=project.id,
                name=project.name,
                mode=project.mode,
                pole_count=len(project.source.poles),
                warning_count=sum(1 for warning in project.warnings if warning.severity != "info"),
                updated_at=project.updated_at,
            ))
        return sorted(summaries, key=lambda item: item.updated_at, reverse=True)
