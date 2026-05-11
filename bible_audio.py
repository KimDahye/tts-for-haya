from __future__ import annotations

import argparse
import sys
from pathlib import Path

from books import Book, resolve_book
from sources import ESVSource, KoreanSource, Verse


def parse_verse_filter(spec: str | None) -> set[int] | None:
    if not spec:
        return None
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


def filter_verses(verses: list[Verse], spec: str | None) -> list[Verse]:
    sel = parse_verse_filter(spec)
    if sel is None:
        return verses
    return [v for v in verses if v[0] in sel]


def chapter_dirname(book: Book, chapter: int, version: str) -> str:
    if version == "esv":
        prefix = book.esv.replace(" ", "_")
    else:
        prefix = book.kor_full
    return f"{prefix}_{chapter}"


def verse_filename(book: Book, chapter: int, verse_no: int, version: str) -> str:
    if version == "esv":
        prefix = book.esv.replace(" ", "_")
    else:
        prefix = book.kor_full
    return f"{prefix}_{chapter}_{verse_no:02d}.mp3"


def full_filename(book: Book, chapter: int, version: str) -> str:
    if version == "esv":
        prefix = book.esv.replace(" ", "_")
    else:
        prefix = book.kor_full
    return f"{prefix}_{chapter}_full.mp3"


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description="ESV / 개역개정 성경 본문을 절별 mp3로 생성합니다."
    )
    parser.add_argument(
        "--version", choices=["esv", "nkrv"], required=True, help="번역본 선택"
    )
    parser.add_argument(
        "--book", required=True, help="책 이름 (예: Jn, John, 요, 요한복음, 43)"
    )
    parser.add_argument("--chapter", type=int, required=True, help="장 번호")
    parser.add_argument(
        "--verses",
        default=None,
        help="절 필터 (예: '16', '1-16', '1,3,5-7'). 생략 시 전체 장",
    )
    parser.add_argument(
        "--no-combine",
        action="store_true",
        help="합친 챕터 mp3를 생성하지 않음",
    )
    parser.add_argument(
        "--gap-ms", type=int, default=700, help="합칠 때 절 사이 무음 길이(ms)"
    )
    parser.add_argument(
        "--out", default="output", help="출력 디렉토리 (기본: ./output)"
    )
    parser.add_argument(
        "--force-engine",
        choices=["eleven", "google"],
        default=None,
        help="영어 TTS 엔진 강제 지정 (자동 라우팅 우회). 미지정 시 FORCE_ENGINE 환경변수 사용",
    )
    parser.add_argument(
        "--ignore-google-limit",
        action="store_true",
        help="Google TTS 월간 무료 한도 사전 검사를 무시 (과금 위험)",
    )
    args = parser.parse_args(argv)

    import os

    if args.force_engine is None:
        env_force = os.environ.get("FORCE_ENGINE", "").strip().lower()
        if env_force in {"eleven", "google"}:
            args.force_engine = env_force

    book = resolve_book(args.book)
    chapter = args.chapter
    version = args.version
    lang = "en" if version == "esv" else "ko"

    if version == "esv":
        source = ESVSource()
    else:
        source = KoreanSource()

    print(f"📖 {book.esv} / {book.kor_full} {chapter}장 본문을 받는 중...")
    verses = source.fetch_chapter(book, chapter)
    verses = filter_verses(verses, args.verses)
    if not verses:
        print("해당 조건에 맞는 절이 없습니다.", file=sys.stderr)
        return 1
    print(f"   → {len(verses)}개 절 확보 (절 {verses[0][0]} ~ {verses[-1][0]})")

    from tts import TTSRouter, GoogleQuotaExceeded

    router = TTSRouter(
        force_engine=args.force_engine,
        ignore_google_limit=args.ignore_google_limit,
    )
    print(f"🎙  TTS 엔진 결정 중 (lang={lang})...")
    try:
        engine, audio_results = router.synthesize_verses(verses, lang=lang)
    except GoogleQuotaExceeded as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2
    print(f"   → 엔진: {engine}")

    out_dir = Path(args.out) / version / chapter_dirname(book, chapter, version)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for (verse_no, audio), (_, text) in zip(audio_results, verses):
        fname = verse_filename(book, chapter, verse_no, version)
        path = out_dir / fname
        path.write_bytes(audio)
        written.append(path)
        preview = text[:30].replace("\n", " ")
        print(f"   [{verse_no:>3}] {preview}{'…' if len(text) > 30 else ''} ✓")

    if not args.no_combine and len(written) > 1:
        full_path = out_dir / full_filename(book, chapter, version)
        print(f"🎧  {len(written)}개 절을 합치는 중 → {full_path.name}")
        from audio import combine_mp3s

        combine_mp3s(written, full_path, gap_ms=args.gap_ms)
        print(f"   → {full_path}")

    print(f"✅ 완료: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
