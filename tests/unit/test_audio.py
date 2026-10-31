"""Unit tests for audio validation and conversion."""

import pytest

from fieldcheck.audio import (
    AudioValidationError,
    compute_sha256,
    convert_and_normalize_audio,
    validate_raw_bytes,
)


def test_empty_audio_rejection() -> None:
    with pytest.raises(AudioValidationError):
        validate_raw_bytes(b"")


def test_size_limit_rejection() -> None:
    with pytest.raises(AudioValidationError):
        validate_raw_bytes(b"0" * 100, max_bytes=50)


def test_sha256_computation() -> None:
    h = compute_sha256(b"hello audio")
    assert len(h) == 64
    assert h == compute_sha256(b"hello audio")


def test_convert_and_normalize_valid_wav() -> None:
    # 0.5s 16kHz mono 16-bit PCM WAV (16000 samples/sec * 0.5s * 2 bytes = 16000 data bytes)
    sample_rate = 16000
    num_samples = 8000
    data_size = num_samples * 2
    header = (
        b"RIFF"
        + (data_size + 36).to_bytes(4, "little")
        + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        + sample_rate.to_bytes(4, "little")
        + (sample_rate * 2).to_bytes(4, "little")
        + b"\x02\x00\x10\x00data"
        + data_size.to_bytes(4, "little")
    )
    wav_bytes = header + (b"\x00" * data_size)

    info = convert_and_normalize_audio(wav_bytes, max_seconds=5.0)
    assert info.sample_rate == 16000
    assert info.channels == 1
    assert 0.4 <= info.duration_seconds <= 0.6
    assert len(info.sha256) == 64
