"""Audio processing, validation, and FFmpeg conversion utilities."""

from __future__ import annotations

import hashlib
import io
import os
import shutil
import subprocess
import tempfile
import wave
from typing import NamedTuple


class AudioInfo(NamedTuple):
    wav_bytes: bytes
    duration_seconds: float
    sha256: str
    sample_rate: int = 16000
    channels: int = 1


class AudioValidationError(Exception):
    """Raised when audio fails security, duration, or format checks."""


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def validate_raw_bytes(data: bytes, max_bytes: int = 10_485_760) -> None:
    """Validate byte length before processing."""
    if not data or len(data) == 0:
        raise AudioValidationError("Audio data is empty")
    if len(data) > max_bytes:
        raise AudioValidationError(
            f"Audio file size ({len(data)} bytes) exceeds limit of {max_bytes} bytes"
        )


def convert_and_normalize_audio(
    raw_data: bytes,
    max_seconds: float = 20.0,
    target_sample_rate: int = 16000,
) -> AudioInfo:
    """Convert input audio (webm, ogg, wav, etc.) to standardized 16kHz mono WAV.

    Enforces duration bounds and returns AudioInfo with duration and hash.
    """
    validate_raw_bytes(raw_data)

    # Already canonical PCM needs validation, not a lossy or expensive round trip.
    try:
        with wave.open(io.BytesIO(raw_data), "rb") as native:
            if (
                native.getnchannels() == 1
                and native.getframerate() == target_sample_rate
                and native.getsampwidth() == 2
                and native.getcomptype() == "NONE"
            ):
                frames = native.getnframes()
                payload = native.readframes(frames)
                if len(payload) != frames * 2:
                    raise AudioValidationError("WAV payload is truncated")
                duration = frames / float(target_sample_rate)
                if duration < 0.2:
                    raise AudioValidationError(
                        f"Audio duration ({duration:.2f}s) is too short or silent"
                    )
                if duration > max_seconds:
                    raise AudioValidationError(
                        f"Audio duration ({duration:.2f}s) exceeds maximum allowed limit ({max_seconds}s)"
                    )
                return AudioInfo(
                    raw_data, round(duration, 3), compute_sha256(raw_data), target_sample_rate, 1
                )
    except (wave.Error, EOFError):
        pass  # Other browser formats still use the existing converter.

    # Serverless fallback when FFmpeg binary is absent (e.g. Vercel Python runtime)
    if shutil.which("ffmpeg") is None:
        try:
            with wave.open(io.BytesIO(raw_data), "rb") as wf:
                channels = wf.getnchannels()
                sample_rate = wf.getframerate()
                frames = wf.getnframes()
                duration = frames / float(sample_rate) if sample_rate > 0 else 0.0

                if duration < 0.2:
                    raise AudioValidationError(
                        f"Audio duration ({duration:.2f}s) is too short or silent"
                    )
                if duration > max_seconds:
                    raise AudioValidationError(
                        f"Audio duration ({duration:.2f}s) exceeds maximum allowed limit ({max_seconds}s)"
                    )

                return AudioInfo(
                    wav_bytes=raw_data,
                    duration_seconds=round(duration, 3),
                    sha256=compute_sha256(raw_data),
                    sample_rate=sample_rate,
                    channels=channels,
                )
        except wave.Error as err:
            raise AudioValidationError(
                f"FFmpeg binary not found on host and input is not valid linear WAV: {err}"
            ) from err

    with tempfile.NamedTemporaryFile(suffix=".input", delete=False) as in_f:
        in_path = in_f.name
        in_f.write(raw_data)

    out_path = in_path + ".wav"

    try:
        # Run ffmpeg to convert to 16kHz mono PCM 16-bit
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i",
            in_path,
            "-ac",
            "1",
            "-ar",
            str(target_sample_rate),
            "-f",
            "wav",
            out_path,
        ]
        try:
            result = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired as te:
            raise AudioValidationError("Audio conversion timed out") from te
        if result.returncode != 0:
            stderr_snippet = result.stderr.decode("utf-8", errors="replace")[-300:]
            raise AudioValidationError(f"Audio conversion failed: {stderr_snippet}")

        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            raise AudioValidationError("Converted audio file is empty or missing")

        # Determine duration: read converted WAV header directly
        try:
            with wave.open(out_path, "rb") as wf:
                duration = wf.getnframes() / float(wf.getframerate())
        except Exception:
            # Fallback to ffprobe if wave header inspection fails
            probe_cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                out_path,
            ]
            probe_res = subprocess.run(
                probe_cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=10,
                check=False,
            )
            try:
                duration = float(probe_res.stdout.decode().strip())
            except ValueError:
                duration = 0.0

        if duration > max_seconds:
            raise AudioValidationError(
                f"Audio duration ({duration:.2f}s) exceeds maximum allowed limit ({max_seconds}s)"
            )
        if duration < 0.2:
            raise AudioValidationError(f"Audio duration ({duration:.2f}s) is too short or silent")

        with open(out_path, "rb") as out_f:
            wav_bytes = out_f.read()

        return AudioInfo(
            wav_bytes=wav_bytes,
            duration_seconds=round(duration, 3),
            sha256=compute_sha256(wav_bytes),
            sample_rate=target_sample_rate,
            channels=1,
        )
    finally:
        for p in (in_path, out_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
