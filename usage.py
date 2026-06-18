from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path(".usage.json")


class UsageTracker:
    """월 단위 character 사용량 추적 (로컬 파일).

    Google TTS 무료 한도는 달력 월(calendar month) 기준으로 리셋되므로, 각 key
    버킷은 "현재 달"의 합계(total)와 호출별 상세 로그(log)만 보관한다. 새로운
    달에 처음 접근하면 지난달 기록을 비우고 이번 달부터 다시 기록한다.

    버킷 구조::

        {
          "google:Chirp3": {
            "month": "2026-06",
            "total": 2552,
            "log": [
              {"at": "2026-06-18T14:03:21", "chars": 1200},
              {"at": "2026-06-18T14:05:09", "chars": 1352}
            ]
          }
        }
    """

    def __init__(self, path: Path | str = DEFAULT_PATH):
        self.path = Path(path)
        self.data: dict[str, dict] = {}
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                self.data = self._migrate(raw)
            except Exception:
                self.data = {}

    @staticmethod
    def current_month() -> str:
        return datetime.now().strftime("%Y-%m")

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    @classmethod
    def _migrate(cls, raw: dict) -> dict:
        """구(舊) 포맷({key: {"YYYY-MM": int}})을 신 포맷으로 변환.

        지난달 값은 어차피 리셋 대상이므로 현재 달 합계만 살린다.
        """
        cur = cls.current_month()
        data: dict[str, dict] = {}
        for key, bucket in (raw or {}).items():
            if not isinstance(bucket, dict):
                continue
            if "month" in bucket and "total" in bucket:
                # 이미 신 포맷
                data[key] = {
                    "month": str(bucket.get("month") or cur),
                    "total": int(bucket.get("total", 0)),
                    "log": list(bucket.get("log", [])),
                }
            else:
                # 구 포맷: 현재 달 값만 이어받는다.
                data[key] = {
                    "month": cur,
                    "total": int(bucket.get(cur, 0)),
                    "log": [],
                }
        return data

    def _bucket(self, key: str) -> dict:
        """현재 달 기준 버킷 반환. 달이 바뀌었으면 지난달 기록을 비우고 새로 시작."""
        cur = self.current_month()
        bucket = self.data.get(key)
        if bucket is not None and bucket.get("month") == cur:
            return bucket
        # 새 달이거나 신규 key → 지난달 기록 제거 후 새 버킷 생성
        existed = bucket is not None
        self.data[key] = {"month": cur, "total": 0, "log": []}
        if existed:
            # 지난달 기록 삭제를 디스크에 즉시 반영 ("이번 달 처음 호출")
            self._save()
        return self.data[key]

    def used(self, key: str) -> int:
        return int(self._bucket(key).get("total", 0))

    def add(self, key: str, chars: int) -> None:
        if chars <= 0:
            return
        bucket = self._bucket(key)
        bucket["total"] = int(bucket.get("total", 0)) + int(chars)
        bucket.setdefault("log", []).append({"at": self._now(), "chars": int(chars)})
        self._save()

    def _save(self) -> None:
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
