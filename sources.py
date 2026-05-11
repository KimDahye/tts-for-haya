from __future__ import annotations

import json
import os
import re
from pathlib import Path

from books import Book

Verse = tuple[int, str]

ESV_API_URL = "https://api.esv.org/v3/passage/text/"


class ESVSource:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ESV_API_KEY")
        if not self.api_key:
            raise RuntimeError("ESV_API_KEY 환경변수가 설정되지 않았습니다.")

    def fetch_chapter(self, book: Book, chapter: int) -> list[Verse]:
        import requests

        passage = f"{book.esv} {chapter}"
        params = {
            "q": passage,
            "include-headings": "false",
            "include-footnotes": "false",
            "include-passage-references": "false",
            "include-short-copyright": "false",
            "include-verse-numbers": "true",
            "include-first-verse-numbers": "true",
            "indent-paragraphs": "0",
            "indent-poetry": "false",
            "indent-poetry-lines": "0",
            "indent-declares": "0",
            "indent-psalm-doxology": "0",
        }
        headers = {"Authorization": f"Token {self.api_key}"}
        resp = requests.get(ESV_API_URL, params=params, headers=headers, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
        passages = payload.get("passages", [])
        if not passages:
            raise RuntimeError(f"ESV API에서 본문을 받지 못했습니다: {passage}")
        return self._parse_verses(passages[0])

    @staticmethod
    def _parse_verses(text: str) -> list[Verse]:
        # ESV API marks verse numbers as [N]. Split on the marker.
        # Find all (verse_no, text) chunks.
        parts = re.split(r"\[(\d+)\]\s*", text)
        # parts: [pre, '1', body1, '2', body2, ...]
        verses: list[Verse] = []
        i = 1
        while i + 1 < len(parts):
            verse_no = int(parts[i])
            body = parts[i + 1]
            body = re.sub(r"\s+", " ", body).strip()
            if body:
                verses.append((verse_no, body))
            i += 2
        return verses


class KoreanSource:
    def __init__(self, bible_json_path: str | Path = "bible.json"):
        path = Path(bible_json_path)
        if not path.exists():
            raise RuntimeError(f"bible.json 파일을 찾을 수 없습니다: {path}")
        with path.open(encoding="utf-8") as f:
            self.data: dict[str, str] = json.load(f)

    def fetch_chapter(self, book: Book, chapter: int) -> list[Verse]:
        verses: list[Verse] = []
        verse_no = 1
        while True:
            key = f"{book.kor_short}{chapter}:{verse_no}"
            text = self.data.get(key)
            if text is None:
                break
            verses.append((verse_no, text.strip()))
            verse_no += 1
        if not verses:
            raise RuntimeError(
                f"bible.json에서 {book.kor_full} {chapter}장을 찾지 못했습니다."
            )
        return verses
