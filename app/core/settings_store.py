"""Persistent JSON settings store under ./data/settings.json."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULTS: Dict[str, Any] = {
    "language": "en",
    "input_folder": "",
    "output_folder": str(Path.home() / "Desktop" / "Done"),
    "audio_folder": "",
    "logo_file": "",
    "overlay_text": "",
    "show_timer": False,
    "blur_background": False,
    "merge": False,
    "cut_plus": False,
    "cut_parts": 2,
    "rename_prefix": "video_",
    "rename_start": 1,
    "audio_mode": "keep",   # keep | mix | mute | random | mp3
    "audio_file": "",
    "encoder": "auto",      # auto | nvenc | amf | cpu
    "cpu_limit": 4,
    "threads_render": 3,
    "output_format": "mp4",
}


class SettingsStore:
    def __init__(self, path: Path = SETTINGS_FILE) -> None:
        self.path = path
        self._data: Dict[str, Any] = dict(DEFAULTS)
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    for k, v in loaded.items():
                        if k in DEFAULTS:
                            self._data[k] = v
            except Exception:
                pass

    def save(self) -> None:
        _atomic_write_text(
            self.path,
            json.dumps(self._data, indent=2, ensure_ascii=False),
        )

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default if default is not None else DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, mapping: Dict[str, Any]) -> None:
        for k, v in mapping.items():
            if k in DEFAULTS:
                self._data[k] = v

    def all(self) -> Dict[str, Any]:
        return dict(self._data)
