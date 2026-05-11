from __future__ import annotations

from pathlib import Path


def combine_mp3s(paths: list[Path], out: Path, gap_ms: int = 700) -> None:
    from pydub import AudioSegment

    if not paths:
        raise ValueError("결합할 mp3 파일이 없습니다.")
    silence = AudioSegment.silent(duration=gap_ms) if gap_ms > 0 else None
    combined = AudioSegment.from_file(paths[0], format="mp3")
    for p in paths[1:]:
        if silence is not None:
            combined += silence
        combined += AudioSegment.from_file(p, format="mp3")
    out.parent.mkdir(parents=True, exist_ok=True)
    combined.export(out, format="mp3")
