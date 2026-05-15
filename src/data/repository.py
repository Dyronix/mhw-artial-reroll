from __future__ import annotations

import json
import os
from pathlib import Path

from data.models import AppState, state_from_dict, state_to_dict


class StateRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> AppState:
        if not self.path.exists():
            return AppState()
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            return AppState()
        return state_from_dict(data)

    def save(self, state: AppState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(state_to_dict(state), file, indent=2, ensure_ascii=False)
            file.write("\n")
        os.replace(temp_path, self.path)
