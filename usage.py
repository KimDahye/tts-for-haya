from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path(".usage.json")


class UsageTracker:
    """월 단위 character 사용량 추적 (로컬 파일)."""

    def __init__(self, path: Path | str = DEFAULT_PATH):
        self.path = Path(path)
        self.data: dict[str, dict[str, int]] = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {}

    @staticmethod
    def current_month() -> str:
        return datetime.now().strftime("%Y-%m")

    def used(self, key: str, month: str | None = None) -> int:
        m = month or self.current_month()
        return int(self.data.get(key, {}).get(m, 0))

    def add(self, key: str, chars: int, month: str | None = None) -> None:
        if chars <= 0:
            return
        m = month or self.current_month()
        bucket = self.data.setdefault(key, {})
        bucket[m] = int(bucket.get(m, 0)) + int(chars)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
