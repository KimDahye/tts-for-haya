from __future__ import annotations

import os
from typing import Literal

from usage import UsageTracker

Lang = Literal["en", "ko"]
Engine = Literal["eleven", "google"]


# Google Cloud TTS 월간 무료 한도 (character).
# 음성 이름의 3번째 토큰(예: "ko-KR-Neural2-A" → "Neural2")으로 매핑.
# 초과 시 단가 — Standard $4/M, Wavenet/Neural2/Polyglot $16/M,
#               Chirp/Chirp3 HD $30/M, Studio $160/M.
GOOGLE_FREE_LIMITS: dict[str, int] = {
    "Standard": 4_000_000,
    "Wavenet": 1_000_000,
    "Neural2": 1_000_000,
    "Polyglot": 1_000_000,
    "Chirp": 1_000_000,
    "Chirp3": 1_000_000,
    "Studio": 100_000,
    "Journey": 100_000,
}


def google_voice_tier(voice_name: str) -> str:
    parts = voice_name.split("-")
    return parts[2] if len(parts) >= 3 else "Standard"


def google_free_limit(voice_name: str) -> int:
    return GOOGLE_FREE_LIMITS.get(google_voice_tier(voice_name), 0)


class GoogleTTS:
    DEFAULT_EN_VOICE = "en-US-Neural2-J"
    DEFAULT_KO_VOICE = "ko-KR-Neural2-A"

    def __init__(
        self,
        en_voice: str | None = None,
        ko_voice: str | None = None,
        speaking_rate: float = 0.95,
        tracker: UsageTracker | None = None,
    ):
        from google.cloud import texttospeech  # type: ignore

        self._tts = texttospeech
        self._client = texttospeech.TextToSpeechClient()
        self.en_voice = en_voice or os.environ.get("GOOGLE_EN_VOICE") or self.DEFAULT_EN_VOICE
        self.ko_voice = ko_voice or os.environ.get("GOOGLE_KO_VOICE") or self.DEFAULT_KO_VOICE
        self.speaking_rate = speaking_rate
        self.tracker = tracker

    def voice_for(self, lang: Lang) -> str:
        return self.ko_voice if lang == "ko" else self.en_voice

    def usage_key(self, lang: Lang) -> str:
        return f"google:{google_voice_tier(self.voice_for(lang))}"

    def remaining_chars(self, lang: Lang) -> int:
        if self.tracker is None:
            return google_free_limit(self.voice_for(lang))
        limit = google_free_limit(self.voice_for(lang))
        used = self.tracker.used(self.usage_key(lang))
        return max(limit - used, 0)

    def synthesize(self, text: str, lang: Lang) -> bytes:
        tts = self._tts
        voice_name = self.voice_for(lang)
        language_code = "-".join(voice_name.split("-")[:2])
        voice = tts.VoiceSelectionParams(language_code=language_code, name=voice_name)
        synthesis_input = tts.SynthesisInput(text=text)
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.MP3,
            speaking_rate=self.speaking_rate,
        )
        resp = self._client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        if self.tracker is not None:
            self.tracker.add(self.usage_key(lang), len(text))
        return resp.audio_content


class ElevenLabsTTS:
    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

    def __init__(
        self,
        api_key: str | None = None,
        voice_id: str | None = None,
        model_id: str = "eleven_multilingual_v2",
    ):
        self.api_key = api_key or os.environ.get("ELEVEN_API_KEY")
        if not self.api_key:
            raise RuntimeError("ELEVEN_API_KEY 환경변수가 설정되지 않았습니다.")
        self.voice_id = (
            voice_id or os.environ.get("ELEVEN_VOICE_ID") or self.DEFAULT_VOICE_ID
        )
        self.model_id = model_id

    def remaining_chars(self) -> int:
        import requests

        resp = requests.get(
            "https://api.elevenlabs.io/v1/user/subscription",
            headers={"xi-api-key": self.api_key},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        limit = int(data.get("character_limit", 0))
        used = int(data.get("character_count", 0))
        return max(limit - used, 0)

    def synthesize(self, text: str, lang: Lang = "en") -> bytes:
        import requests

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        resp = requests.post(
            url,
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            params={"output_format": "mp3_44100_128"},
            json={
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                },
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.content


class GoogleQuotaExceeded(RuntimeError):
    pass


class TTSRouter:
    def __init__(
        self,
        force_engine: Engine | None = None,
        tracker: UsageTracker | None = None,
        ignore_google_limit: bool = False,
    ):
        self.force_engine = force_engine
        self.tracker = tracker or UsageTracker()
        self.ignore_google_limit = ignore_google_limit
        self._google: GoogleTTS | None = None
        self._eleven: ElevenLabsTTS | None = None

    @property
    def google(self) -> GoogleTTS:
        if self._google is None:
            self._google = GoogleTTS(tracker=self.tracker)
        return self._google

    @property
    def eleven(self) -> ElevenLabsTTS:
        if self._eleven is None:
            self._eleven = ElevenLabsTTS()
        return self._eleven

    def _check_google_quota(self, need: int, lang: Lang) -> None:
        if self.ignore_google_limit:
            return
        voice = self.google.voice_for(lang)
        limit = google_free_limit(voice)
        used = self.tracker.used(self.google.usage_key(lang))
        remaining = max(limit - used, 0)
        tier = google_voice_tier(voice)
        if limit == 0:
            raise GoogleQuotaExceeded(
                f"Google 음성 '{voice}'(tier={tier})는 무료 한도가 없습니다. "
                f"--ignore-google-limit 으로 강제할 수 있지만 과금됩니다."
            )
        if need > remaining:
            raise GoogleQuotaExceeded(
                f"Google TTS 무료 한도 부족: "
                f"tier={tier}, used={used:,}, limit={limit:,}, "
                f"remaining={remaining:,}, need={need:,}. "
                f"이번 달에는 호출하지 않습니다. "
                f"강제 진행하려면 --ignore-google-limit."
            )
        print(
            f"[engine] Google {tier} (remaining: {remaining:,} / need: {need:,})"
        )

    def choose_engine(self, verses_text: list[str], lang: Lang) -> Engine:
        need = sum(len(t) for t in verses_text)
        if lang == "ko":
            self._check_google_quota(need, lang)
            return "google"
        if self.force_engine == "google":
            self._check_google_quota(need, lang)
            return "google"
        if self.force_engine == "eleven":
            return "eleven"
        # 자동 라우팅: ElevenLabs 잔여 우선 확인
        try:
            remaining = self.eleven.remaining_chars()
        except Exception as e:
            print(f"⚠ ElevenLabs 잔여 한도 조회 실패 ({e}) — Google TTS로 폴백 시도")
            self._check_google_quota(need, lang)
            return "google"
        if need <= remaining:
            print(
                f"[engine] ElevenLabs (remaining: {remaining:,} / need: {need:,})"
            )
            return "eleven"
        print(
            f"⚠ ElevenLabs 잔여 {remaining:,}자 < 필요 {need:,}자 — Google TTS로 폴백"
        )
        self._check_google_quota(need, lang)
        return "google"

    def synthesize_verses(
        self, verses: list[tuple[int, str]], lang: Lang
    ) -> tuple[Engine, list[tuple[int, bytes]]]:
        texts = [t for _, t in verses]
        engine = self.choose_engine(texts, lang)
        results: list[tuple[int, bytes]] = []
        for verse_no, text in verses:
            if engine == "eleven":
                audio = self.eleven.synthesize(text, lang)
            else:
                audio = self.google.synthesize(text, lang)
            results.append((verse_no, audio))
        return engine, results
