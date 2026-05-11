"""본인 ElevenLabs 계정에서 바로 사용 가능한 voice 목록을 표로 출력.

usage:
    python list_voices.py                  # 전체
    python list_voices.py --accent british # 액센트 필터
    python list_voices.py --gender female  # 성별 필터
    python list_voices.py --accent british --gender female
"""
from __future__ import annotations

import argparse
import os
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accent", default=None, help="액센트 필터 (예: british, american)")
    parser.add_argument("--gender", default=None, help="성별 필터 (예: female, male)")
    parser.add_argument("--category", default=None, help="카테고리 필터 (예: premade, cloned)")
    args = parser.parse_args()

    api_key = os.environ.get("ELEVEN_API_KEY")
    if not api_key:
        print("ELEVEN_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        return 1

    import requests

    resp = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key},
        timeout=20,
    )
    resp.raise_for_status()
    voices = resp.json().get("voices", [])

    rows: list[tuple[str, str, str, str, str]] = []
    for v in voices:
        labels = v.get("labels") or {}
        accent = (labels.get("accent") or "").lower()
        gender = (labels.get("gender") or labels.get("Gender") or "").lower()
        category = (v.get("category") or "").lower()

        if args.accent and args.accent.lower() not in accent:
            continue
        if args.gender and args.gender.lower() not in gender:
            continue
        if args.category and args.category.lower() not in category:
            continue

        rows.append(
            (
                v.get("name", ""),
                v.get("voice_id", ""),
                category,
                accent,
                gender,
            )
        )

    if not rows:
        print("조건에 맞는 voice가 없습니다. 필터를 풀고 다시 시도해보세요.")
        return 0

    # column widths
    headers = ("Name", "Voice ID", "Category", "Accent", "Gender")
    widths = [max(len(h), max(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for r in rows:
        print(fmt.format(*r))
    print(f"\n총 {len(rows)}개 voice (전체 {len(voices)}개 중 필터 적용)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
