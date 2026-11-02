"""Gnani Prisma STT and Timbre TTS provider adapter."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import shutil
import subprocess
import tempfile
import time

import httpx

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from sureword.contracts import Transcript

logger = logging.getLogger("sureword.providers.gnani")

# Provider lock to serialize calls and protect 1-concurrent request accounts
_PROVIDER_LOCK = asyncio.Lock()


class GnaniProviderError(Exception):
    """Raised on Gnani API failure or configuration error."""

    def __init__(
        self,
        message: str,
        code: str = "PROVIDER_ERROR",
        retryable: bool = False,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.status_code = status_code


class GnaniClient:
    def __init__(
        self,
        api_key: str | None = None,
        stt_url: str | None = None,
        tts_url: str | None = None,
        stt_model: str | None = None,
        tts_model: str | None = None,
        tts_voice: str | None = None,
        default_language: str | None = None,
        allow_fixture_fallback: bool | None = None,
    ) -> None:
        self.api_key: str = (
            api_key if api_key is not None else (os.getenv("GNANI_API_KEY") or "")
        )
        self.stt_url: str = (
            stt_url
            if stt_url is not None
            else (os.getenv("GNANI_STT_URL") or "https://api.vachana.ai/stt/v3")
        )
        self.tts_url: str = (
            tts_url
            if tts_url is not None
            else (os.getenv("GNANI_TTS_URL") or "https://api.vachana.ai/api/v1/tts/inference")
        )
        self.stt_model: str = (
            stt_model
            if stt_model is not None
            else (os.getenv("GNANI_STT_MODEL") or "prisma-v3.0")
        )
        self.tts_model: str = (
            tts_model
            if tts_model is not None
            else (os.getenv("GNANI_TTS_MODEL") or "timbre-v2.5")
        )
        self.tts_voice: str = (
            tts_voice
            if tts_voice is not None
            else (os.getenv("GNANI_TTS_VOICE") or "Bhavna")
        )
        self.default_language: str = (
            default_language
            if default_language is not None
            else (os.getenv("GNANI_LANGUAGE") or "hi-IN")
        )
        self.allow_fixture_fallback: bool = (
            allow_fixture_fallback
            if allow_fixture_fallback is not None
            else (os.getenv("ALLOW_FIXTURE_FALLBACK", "true").lower() in ("true", "1", "yes"))
        )

    def has_credentials(self) -> bool:
        """Check whether valid non-placeholder API key is set."""
        return bool(
            self.api_key and self.api_key.strip() and "your_gnani_api_key" not in self.api_key
        )

    async def transcribe_audio(
        self,
        wav_bytes: bytes,
        language: str | None = None,
        retries: int = 2,
    ) -> Transcript:
        """Transcribe mono WAV audio via Gnani Prisma."""
        lang = language or self.default_language

        if not self.has_credentials():
            if self.allow_fixture_fallback:
                logger.info(
                    "No Gnani API key configured. Using deterministic fixture transcription."
                )
                fixture_text = os.getenv(
                    "FIXTURE_TRANSCRIPT",
                    "मरीज का नाम कमला देवी है, उम्र 150 साल, गाँव रामपुर, विजिट डेट 30 अक्टूबर 2026",
                )
                return Transcript(
                    text=fixture_text,
                    provider="gnani_prisma",
                    requested_model=self.stt_model,
                    effective_model=f"{self.stt_model}-fixture",
                    request_id="fixture-stt-001",
                    duration_ms=450.0,
                    confidence=0.89,
                    source="fixture",
                )
            raise GnaniProviderError(
                "Missing Gnani API key (GNANI_API_KEY). Set your key in .env or environment.",
                code="AUTH_MISSING",
                retryable=False,
            )

        headers: dict[str, str] = {
            "X-API-Key-ID": self.api_key,
        }

        files = {
            "audio_file": ("audio.wav", wav_bytes, "audio/wav"),
        }
        data = {
            "language_code": lang,
            "model": self.stt_model,
        }

        async with _PROVIDER_LOCK:
            start_t = time.perf_counter()
            for attempt in range(retries + 1):
                try:
                    async with httpx.AsyncClient(
                        timeout=httpx.Timeout(20.0, connect=5.0)
                    ) as client:
                        resp = await client.post(
                            self.stt_url,
                            headers=headers,
                            data=data,
                            files=files,
                        )

                    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

                    if resp.status_code == 200:
                        res_json = resp.json()
                        transcript_text = (
                            res_json.get("transcript")
                            or res_json.get("text")
                            or res_json.get("data", {}).get("transcript")
                            or ""
                        )
                        req_id = resp.headers.get("x-request-id", res_json.get("request_id"))
                        confidence = res_json.get("confidence")
                        return Transcript(
                            text=transcript_text.strip(),
                            provider="gnani_prisma",
                            requested_model=self.stt_model,
                            effective_model=res_json.get("model", self.stt_model),
                            request_id=req_id,
                            duration_ms=round(elapsed_ms, 2),
                            confidence=confidence,
                            source="live",
                        )

                    if resp.status_code in {429, 502, 503, 504} and attempt < retries:
                        backoff = 1.0 * (2**attempt)
                        logger.warning(
                            "Gnani STT returned HTTP %s. Retrying in %ss (attempt %s/%s)...",
                            resp.status_code,
                            backoff,
                            attempt + 1,
                            retries,
                        )
                        await asyncio.sleep(backoff)
                        continue

                    raise GnaniProviderError(
                        f"Gnani STT API error (HTTP {resp.status_code}): {resp.text[:200]}",
                        code=f"HTTP_{resp.status_code}",
                        retryable=(resp.status_code in {429, 500, 502, 503, 504}),
                        status_code=resp.status_code,
                    )
                except httpx.TimeoutException as te:
                    if attempt < retries:
                        await asyncio.sleep(1.0)
                        continue
                    raise GnaniProviderError(
                        "Gnani STT connection/read timed out after 20 seconds",
                        code="TIMEOUT",
                        retryable=True,
                    ) from te
                except httpx.RequestError as re:
                    if attempt < retries:
                        await asyncio.sleep(1.0)
                        continue
                    raise GnaniProviderError(
                        f"Gnani STT network error: {re}",
                        code="NETWORK_ERROR",
                        retryable=True,
                    ) from re

        raise GnaniProviderError("Gnani STT failed after maximum retries", code="RETRIES_EXHAUSTED")

    async def synthesize_speech(
        self,
        text: str,
        language: str | None = None,
        retries: int = 2,
    ) -> bytes:
        """Synthesize spoken text via Gnani Timbre."""
        lang = language or self.default_language

        if not self.has_credentials():
            if self.allow_fixture_fallback:
                logger.info("No Gnani API key configured. Generating speech synthesis fallback.")
                espeak_bin = shutil.which("espeak") or shutil.which("espeak-ng")
                if espeak_bin:
                    tmp_wav = ""
                    try:
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                            tmp_wav = f.name
                        res = subprocess.run(
                            [espeak_bin, "-w", tmp_wav, "-v", lang[:2], text],
                            capture_output=True,
                            stdin=subprocess.DEVNULL,
                            timeout=5,
                            check=False,
                        )
                        if (
                            res.returncode == 0
                            and os.path.exists(tmp_wav)
                            and os.path.getsize(tmp_wav) > 44
                        ):
                            with open(tmp_wav, "rb") as out_f:
                                return out_f.read()
                    except Exception as ex:
                        logger.warning(
                            "Local espeak fallback failed: %s; using minimal WAV header", ex
                        )
                    finally:
                        if tmp_wav and os.path.exists(tmp_wav):
                            try:
                                os.remove(tmp_wav)
                            except OSError:
                                pass

                # Minimal valid 44-byte mono 8kHz PCM WAV header
                return (
                    b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
                    b"@\x1f\x00\x00\x80>\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
                )
            raise GnaniProviderError(
                "Missing Gnani API key (GNANI_API_KEY). Set your key in .env or environment.",
                code="AUTH_MISSING",
                retryable=False,
            )

        headers: dict[str, str] = {
            "X-API-Key-ID": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model": self.tts_model,
            "voice": self.tts_voice,
            "audio_config": {
                "encoding": "linear_pcm",
                "container": "wav",
                "num_channels": 1,
                "sample_rate": 16000,
                "sample_width": 2,
            },
        }

        async with _PROVIDER_LOCK:
            for attempt in range(retries + 1):
                try:
                    async with httpx.AsyncClient(
                        timeout=httpx.Timeout(15.0, connect=5.0)
                    ) as client:
                        resp = await client.post(
                            self.tts_url,
                            headers=headers,
                            json=payload,
                        )

                    if resp.status_code == 200:
                        content_type = resp.headers.get("content-type", "")
                        if "audio" in content_type or "octet-stream" in content_type:
                            return resp.content
                        # In case audio is returned in json base64 field
                        try:
                            rj = resp.json()
                            audio_b64 = rj.get("audio_content") or rj.get("audio") or ""
                            return base64.b64decode(audio_b64)
                        except Exception:
                            return resp.content

                    if resp.status_code in {429, 502, 503, 504} and attempt < retries:
                        backoff = 1.0 * (2**attempt)
                        await asyncio.sleep(backoff)
                        continue

                    raise GnaniProviderError(
                        f"Gnani TTS API error (HTTP {resp.status_code}): {resp.text[:200]}",
                        code=f"HTTP_{resp.status_code}",
                        retryable=(resp.status_code in {429, 500, 502, 503, 504}),
                        status_code=resp.status_code,
                    )
                except (httpx.TimeoutException, httpx.RequestError) as ex:
                    if attempt < retries:
                        await asyncio.sleep(1.0)
                        continue
                    raise GnaniProviderError(
                        f"Gnani TTS communication error: {ex}",
                        code="TTS_NETWORK_ERROR",
                        retryable=True,
                    ) from ex

        raise GnaniProviderError("Gnani TTS failed after maximum retries", code="RETRIES_EXHAUSTED")
