"""Integration tests for Gnani client adapter."""

import pytest

from fieldcheck.providers.gnani import GnaniClient, GnaniProviderError


@pytest.mark.asyncio
async def test_fixture_fallback_when_unconfigured() -> None:
    client = GnaniClient(api_key="", allow_fixture_fallback=True)
    assert not client.has_credentials()

    transcript = await client.transcribe_audio(b"dummy")
    assert transcript.source == "fixture"
    assert "कमला देवी" in transcript.text

    tts_audio = await client.synthesize_speech("नमस्ते")
    assert len(tts_audio) > 0
    assert tts_audio.startswith(b"RIFF")


@pytest.mark.asyncio
async def test_error_when_fallback_disabled_and_no_key() -> None:
    client = GnaniClient(api_key="", allow_fixture_fallback=False)
    with pytest.raises(GnaniProviderError) as exc_info:
        await client.transcribe_audio(b"dummy")
    assert exc_info.value.code == "AUTH_MISSING"
