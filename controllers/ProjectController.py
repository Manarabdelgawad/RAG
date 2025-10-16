from typing import Dict, List


class ProjectController:
    """Minimal stub to satisfy ProcessController dependencies."""

    def __init__(self):
        self._store: Dict[str, List] = {}
        self._current_project_id: str = "default"
        self._ensure_project(self._current_project_id)

    def _ensure_project(self, project_id: str) -> None:
        if project_id not in self._store:
            self._store[project_id] = []

    def get_current_project_id(self) -> str:
        return self._current_project_id

    def reset_project_data(self, project_id: str) -> None:
        self._store[project_id] = []

    def add_documents_to_project(self, project_id: str, docs: List) -> None:
        self._ensure_project(project_id)
        self._store[project_id].extend(docs)

