"""Integration tests for Gnani client adapter."""

import pytest

from sureword.providers.gnani import GnaniClient, GnaniProviderError


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

    with pytest.raises(GnaniProviderError) as exc_tts:
        await client.synthesize_speech("नमस्ते")
    assert exc_tts.value.code == "AUTH_MISSING"


@pytest.mark.asyncio
async def test_transcribe_audio_live_mock_200() -> None:
    from unittest.mock import patch

    import httpx

    client = GnaniClient(api_key="mock_key")
    real_response = httpx.Response(
        status_code=200,
        headers={"x-request-id": "req_123"},
        json={
            "transcript": "मरीज का नाम कमला देवी",
            "model": "prisma-v3",
            "confidence": 0.95,
        },
    )

    with patch("httpx.AsyncClient.post", return_value=real_response):
        res = await client.transcribe_audio(b"fake_wav_bytes")
        assert res.source == "live"
        assert res.text == "मरीज का नाम कमला देवी"
        assert res.confidence == 0.95
        assert res.request_id == "req_123"


@pytest.mark.asyncio
async def test_transcribe_audio_retry_and_timeout() -> None:
    from unittest.mock import patch

    import httpx

    client = GnaniClient(api_key="mock_key")

    # 1. Server error 500
    mock_500 = httpx.Response(status_code=500, text="Internal error")
    with patch("httpx.AsyncClient.post", return_value=mock_500):
        with pytest.raises(GnaniProviderError) as exc_500:
            await client.transcribe_audio(b"fake_wav_bytes", retries=0)
        assert exc_500.value.code == "HTTP_500"

    # 2. Timeout error
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("timeout")):
        with pytest.raises(GnaniProviderError) as exc_to:
            await client.transcribe_audio(b"fake_wav_bytes", retries=0)
        assert exc_to.value.code == "TIMEOUT"

    # 3. Network error
    with patch("httpx.AsyncClient.post", side_effect=httpx.RequestError("connect fail")):
        with pytest.raises(GnaniProviderError) as exc_net:
            await client.transcribe_audio(b"fake_wav_bytes", retries=0)
        assert exc_net.value.code == "NETWORK_ERROR"


@pytest.mark.asyncio
async def test_synthesize_speech_live_mock() -> None:
    import base64
    from unittest.mock import patch

    import httpx

    client = GnaniClient(api_key="mock_key")

    # 1. Binary audio/wav response
    mock_bin = httpx.Response(
        status_code=200,
        headers={"content-type": "audio/wav"},
        content=b"RIFF_FAKE_AUDIO",
    )
    with patch("httpx.AsyncClient.post", return_value=mock_bin):
        audio = await client.synthesize_speech("नमस्ते", retries=0)
        assert audio == b"RIFF_FAKE_AUDIO"

    # 2. JSON base64 audio response
    raw_audio = b"RIFF_JSON_AUDIO"
    mock_json = httpx.Response(
        status_code=200,
        headers={"content-type": "application/json"},
        json={"audio_content": base64.b64encode(raw_audio).decode()},
    )
    with patch("httpx.AsyncClient.post", return_value=mock_json):
        audio_j = await client.synthesize_speech("नमस्ते", retries=0)
        assert audio_j == raw_audio

    # 3. Network / Request error
    with patch("httpx.AsyncClient.post", side_effect=httpx.RequestError("TTS network fail")):
        with pytest.raises(GnaniProviderError) as exc_net:
            await client.synthesize_speech("नमस्ते", retries=0)
        assert exc_net.value.code == "TTS_NETWORK_ERROR"

    # 4. HTTP 500 error
    mock_500 = httpx.Response(status_code=500, text="TTS backend crash")
    with patch("httpx.AsyncClient.post", return_value=mock_500):
        with pytest.raises(GnaniProviderError) as exc_500:
            await client.synthesize_speech("नमस्ते", retries=0)
        assert exc_500.value.code == "HTTP_500"
