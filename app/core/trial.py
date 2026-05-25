"""30-day free trial counter, persisted under ./data/trial.json."""
from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)

TRIAL_DAYS = 30
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
TRIAL_FILE = DATA_DIR / "trial.json"


class Trial:
    def __init__(self, path: Path = TRIAL_FILE, days: int = TRIAL_DAYS) -> None:
        self.path = path
        self.days = days
        self.start_date: date = date.today()
        self._load_or_init()

    def _load_or_init(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.start_date = date.fromisoformat(data["start_date"])
                return
            except Exception:
                pass
        self.start_date = date.today()
        self._save()

    def _save(self) -> None:
        _atomic_write_text(
            self.path,
            json.dumps(
                {
                    "start_date": self.start_date.isoformat(),
                    "saved_at": datetime.now().isoformat(timespec="seconds"),
                },
                indent=2,
            ),
        )

    def days_remaining(self) -> int:
        used = (date.today() - self.start_date).days
        remaining = self.days - used
        return max(0, remaining)

    def is_expired(self) -> bool:
        return self.days_remaining() <= 0
