# tts-for-haya
ESV / 개역개정 성경 한 장을 절별 mp3 + 합본 mp3로 생성하는 개인용 CLI.

## 빠른 시작

```bash
# 1. ffmpeg (mp3 병합용)
brew install ffmpeg

# 2. 파이썬 의존성
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 환경변수
cp .env.example .env
# .env 채우기: ESV_API_KEY, GOOGLE_APPLICATION_CREDENTIALS, ELEVEN_API_KEY
```

### API 키 발급

- **ESV**: https://api.esv.org/ — 가입 후 토큰 발급 (무료)
- **Google Cloud TTS**: GCP 프로젝트 → Text-to-Speech API 활성화 → 서비스 계정 키 JSON 다운로드 → 경로를 `GOOGLE_APPLICATION_CREDENTIALS`에
- **ElevenLabs**: https://elevenlabs.io/ — 무료 플랜 월 10,000자

## 사용법

```bash
# 요한복음 3장 전체 (한글)
python bible_audio.py --version nkrv --book 요 --chapter 3

# 요한복음 3:16 한 절만 (영어, ESV)
python bible_audio.py --version esv --book Jn --chapter 3 --verses 16

# 시편 23편 (책 이름은 풀네임/약어/한글/숫자 모두 가능)
python bible_audio.py --version nkrv --book 시편 --chapter 23
python bible_audio.py --version esv --book Ps --chapter 23
python bible_audio.py --version esv --book 19 --chapter 23

# 합친 mp3 만들지 않고 절별 파일만
python bible_audio.py --version esv --book Jn --chapter 3 --no-combine

# 영어 TTS 엔진 강제 지정
python bible_audio.py --version esv --book Jn --chapter 3 --force-engine google
```

## 영어 TTS 자동 라우팅

영어(ESV)는 매 실행마다:
1. ElevenLabs `/v1/user/subscription`로 잔여 character 조회
2. 이번 장 글자수 ≤ 잔여 → ElevenLabs 사용
3. 글자수 > 잔여 → Google TTS로 자동 폴백 (안내 메시지 출력)

같은 장 안에서 음성이 섞이지 않도록 장 단위로 한 엔진만 사용.

한글(개역개정)은 항상 Google Cloud TTS (`ko-KR-Neural2-A`).

## 출력 구조

```
output/
└── esv/
    └── John_3/
        ├── John_3_01.mp3
        ├── John_3_02.mp3
        ├── ...
        └── John_3_full.mp3
```
