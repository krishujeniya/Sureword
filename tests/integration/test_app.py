"""Integration tests for Sureword FastAPI endpoints."""

import os
import tempfile
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from sureword.app import app, storage


@pytest.fixture(autouse=True)
async def init_test_db() -> AsyncGenerator[None, None]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    storage.db_path = db_path
    await storage.init_db()
    yield
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.mark.asyncio
async def test_health_check() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/healthz")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["database"] == "sqlite_ready"


@pytest.mark.asyncio
async def test_full_draft_lifecycle() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create draft
        res = await client.post("/api/drafts")
        assert res.status_code == 200
        draft_info = res.json()
        draft_id = draft_info["draft_id"]
        v = draft_info["version"]

        # 2. Upload valid audio (0.5s mono 16kHz WAV)
        num_samples = 8000
        data_size = num_samples * 2
        header = (
            b"RIFF"
            + (data_size + 36).to_bytes(4, "little")
            + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            + (16000).to_bytes(4, "little")
            + (32000).to_bytes(4, "little")
            + b"\x02\x00\x10\x00data"
            + data_size.to_bytes(4, "little")
        )
        wav_bytes = header + (b"\x00" * data_size)

        files = {"audio_file": ("test.wav", wav_bytes, "audio/wav")}
        data = {"expected_version": v}

        res = await client.post(f"/api/drafts/{draft_id}/audio", data=data, files=files)
        assert res.status_code == 200
        audio_res = res.json()
        updated_draft = audio_res["draft"]
        new_v = updated_draft["version"]
        assert new_v > v

        # 3. Test clarify via manual edit for fields requiring clarification
        # First verify that attempting to commit while clarification is pending is rejected with 400
        res_commit_premature = await client.post(
            f"/api/drafts/{draft_id}/commit",
            json={
                "expected_version": new_v,
                "idempotency_key": "premature_attempt",
            },
        )
        assert res_commit_premature.status_code == 400
        assert "clarification is pending" in res_commit_premature.json()["detail"]

        # Clarify fields until state reaches READY_FOR_REVIEW
        curr_v = new_v
        curr_draft = updated_draft
        while curr_draft["state"] == "NEEDS_CLARIFICATION" and curr_draft.get("active_prompt"):
            target = curr_draft["active_prompt"]["target_field"]
            existing_val = curr_draft["fields"][target]["canonical_value"] or "Test Val"
            res_clarify = await client.post(
                f"/api/drafts/{draft_id}/clarify",
                data={
                    "target_field": target,
                    "expected_version": curr_v,
                    "manual_value": existing_val,
                },
            )
            assert res_clarify.status_code == 200
            curr_draft = res_clarify.json()
            curr_v = curr_draft["version"]

        assert curr_draft["state"] == "READY_FOR_REVIEW"

        # 4. Commit draft once ready for review
        res_commit = await client.post(
            f"/api/drafts/{draft_id}/commit",
            json={
                "expected_version": curr_v,
                "idempotency_key": "idemp_test_full_flow",
            },
        )
        assert res_commit.status_code == 200
        commit_res = res_commit.json()
        assert commit_res["status"] == "COMMITTED"
        assert commit_res["record_id"].startswith("REC-")


@pytest.mark.asyncio
async def test_ui_index_served() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
        assert "Sureword" in res.text


@pytest.mark.asyncio
async def test_get_draft_endpoints() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. 404 for non-existent draft
        res_404 = await client.get("/api/drafts/non_existent_123")
        assert res_404.status_code == 404
        assert res_404.json()["detail"] == "Draft not found"

        # 2. 200 for existing draft
        res_create = await client.post("/api/drafts")
        assert res_create.status_code == 200
        draft_id = res_create.json()["draft_id"]

        res_get = await client.get(f"/api/drafts/{draft_id}")
        assert res_get.status_code == 200
        assert res_get.json()["draft_id"] == draft_id


@pytest.mark.asyncio
async def test_process_audio_error_branches() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_create = await client.post("/api/drafts")
        draft_id = res_create.json()["draft_id"]
        v = res_create.json()["version"]

        # 1. Too short / invalid audio -> 400
        files_bad = {"audio_file": ("bad.wav", b"too_short", "audio/wav")}
        res_bad = await client.post(
            f"/api/drafts/{draft_id}/audio", data={"expected_version": v}, files=files_bad
        )
        assert res_bad.status_code == 400

        # 2. Stale version -> 409
        # Create valid 0.5s audio
        num_samples = 8000
        data_size = num_samples * 2
        header = (
            b"RIFF"
            + (data_size + 36).to_bytes(4, "little")
            + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            + (16000).to_bytes(4, "little")
            + (32000).to_bytes(4, "little")
            + b"\x02\x00\x10\x00data"
            + data_size.to_bytes(4, "little")
        )
        valid_wav = header + (b"\x00" * data_size)
        files_valid = {"audio_file": ("good.wav", valid_wav, "audio/wav")}

        res_stale = await client.post(
            f"/api/drafts/{draft_id}/audio",
            data={"expected_version": 999},  # Stale
            files=files_valid,
        )
        assert res_stale.status_code == 409


@pytest.mark.asyncio
async def test_clarify_field_branches() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_create = await client.post("/api/drafts")
        draft_id = res_create.json()["draft_id"]
        v = res_create.json()["version"]

        # 1. Missing both manual_value and audio_file -> 400
        res_no_payload = await client.post(
            f"/api/drafts/{draft_id}/clarify",
            data={"target_field": "person_name", "expected_version": v},
        )
        assert res_no_payload.status_code == 400

        # 2. Audio clarification with spoken repeat
        num_samples = 8000
        data_size = num_samples * 2
        header = (
            b"RIFF"
            + (data_size + 36).to_bytes(4, "little")
            + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            + (16000).to_bytes(4, "little")
            + (32000).to_bytes(4, "little")
            + b"\x02\x00\x10\x00data"
            + data_size.to_bytes(4, "little")
        )
        valid_wav = header + (b"\x00" * data_size)
        files_audio = {"audio_file": ("repeat.wav", valid_wav, "audio/wav")}

        res_audio_clarify = await client.post(
            f"/api/drafts/{draft_id}/clarify",
            data={"target_field": "person_name", "expected_version": v},
            files=files_audio,
        )
        assert res_audio_clarify.status_code == 200
        new_v = res_audio_clarify.json()["version"]
        assert new_v > v

        # 3. Clarification with stale version -> 409
        res_stale_clarify = await client.post(
            f"/api/drafts/{draft_id}/clarify",
            data={
                "target_field": "person_name",
                "expected_version": 999,
                "manual_value": "Kamla Devi",
            },
        )
        assert res_stale_clarify.status_code == 409

        # 4. Audio clarification for other fields: age, village, visit_date
        for field in ["age", "village", "visit_date"]:
            res_f = await client.post(
                f"/api/drafts/{draft_id}/clarify",
                data={"target_field": field, "expected_version": new_v},
                files=files_audio,
            )
            assert res_f.status_code == 200
            new_v = res_f.json()["version"]

        # 5. Audio clarification with unknown field -> 400
        res_unk = await client.post(
            f"/api/drafts/{draft_id}/clarify",
            data={"target_field": "unknown_field_xyz", "expected_version": new_v},
            files=files_audio,
        )
        assert res_unk.status_code == 400


@pytest.mark.asyncio
async def test_speech_synthesis_endpoint() -> None:
    from unittest.mock import patch

    from sureword.contracts import ClarificationPrompt
    from sureword.providers.gnani import GnaniProviderError

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Speech for non-existent draft -> 404
        res_nf = await client.post("/api/drafts/missing_123/speech")
        assert res_nf.status_code == 404

        # 2. Speech for draft with NO active prompt -> 400
        res_create = await client.post("/api/drafts")
        draft_id = res_create.json()["draft_id"]
        res_no_prompt = await client.post(f"/api/drafts/{draft_id}/speech")
        assert res_no_prompt.status_code == 400
        assert "no active clarification prompt" in res_no_prompt.json()["detail"]

        # 3. Speech for draft WITH active prompt -> 200 audio/wav
        draft = await storage.get_draft(draft_id)
        assert draft is not None
        draft.active_prompt = ClarificationPrompt(
            target_field="age",
            prompt_text="उम्र स्पष्ट करें",
            attempt_number=1,
        )
        await storage.save_draft(draft, event_type="TEST_PROMPT")

        res_speech = await client.post(f"/api/drafts/{draft_id}/speech")
        assert res_speech.status_code == 200
        assert res_speech.headers["content-type"] == "audio/wav"

        # 4. Speech when TTS provider raises GnaniProviderError -> 502
        with patch.object(
            app.state if hasattr(app, "state") else None or storage,
            "__class__",
        ):
            pass
        from sureword.app import gnani_client

        with patch.object(
            gnani_client,
            "synthesize_speech",
            side_effect=GnaniProviderError("Simulated TTS failure"),
        ):
            res_tts_err = await client.post(f"/api/drafts/{draft_id}/speech")
            assert res_tts_err.status_code == 502


@pytest.mark.asyncio
async def test_provider_errors_in_audio_endpoints() -> None:
    from unittest.mock import patch

    from sureword.app import gnani_client
    from sureword.providers.gnani import GnaniProviderError

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_create = await client.post("/api/drafts")
        draft_id = res_create.json()["draft_id"]
        v = res_create.json()["version"]

        num_samples = 8000
        data_size = num_samples * 2
        header = (
            b"RIFF"
            + (data_size + 36).to_bytes(4, "little")
            + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            + (16000).to_bytes(4, "little")
            + (32000).to_bytes(4, "little")
            + b"\x02\x00\x10\x00data"
            + data_size.to_bytes(4, "little")
        )
        valid_wav = header + (b"\x00" * data_size)
        files_audio = {"audio_file": ("test.wav", valid_wav, "audio/wav")}

        # 1. /audio endpoint when STT provider fails -> 502
        with patch.object(
            gnani_client,
            "transcribe_audio",
            side_effect=GnaniProviderError("Simulated STT error", status_code=502),
        ):
            res_audio_err = await client.post(
                f"/api/drafts/{draft_id}/audio",
                data={"expected_version": v},
                files=files_audio,
            )
            assert res_audio_err.status_code == 502

        # 2. /clarify endpoint with audio when STT provider fails -> 502
        with patch.object(
            gnani_client,
            "transcribe_audio",
            side_effect=GnaniProviderError("Simulated STT error"),
        ):
            res_clarify_err = await client.post(
                f"/api/drafts/{draft_id}/clarify",
                data={"target_field": "person_name", "expected_version": v},
                files=files_audio,
            )
            assert res_clarify_err.status_code == 502


@pytest.mark.asyncio
async def test_ui_index_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import patch

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("os.path.exists", return_value=False):
            res = await client.get("/")
            assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_and_commit_errors() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_create = await client.post("/api/drafts")
        draft_id = res_create.json()["draft_id"]

        # Commit with stale version -> 409
        res_commit_stale = await client.post(
            f"/api/drafts/{draft_id}/commit",
            json={"expected_version": 999, "idempotency_key": "stale_k"},
        )
        assert res_commit_stale.status_code == 409

        # Delete draft -> 204
        res_del = await client.delete(f"/api/drafts/{draft_id}")
        assert res_del.status_code == 204

        # Verify draft is deleted -> 404
        res_get_del = await client.get(f"/api/drafts/{draft_id}")
        assert res_get_del.status_code == 404


@pytest.mark.asyncio
async def test_get_committed_records_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/records")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_audio_endpoint_with_simulated_transcript() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_create = await client.post("/api/drafts")
        draft_id = res_create.json()["draft_id"]
        v = res_create.json()["version"]

        res_sim = await client.post(
            f"/api/drafts/{draft_id}/audio",
            data={
                "expected_version": v,
                "simulated_transcript": "मरीज का नाम कमला देवी है, उम्र पैंतालीस साल, गाँव रामपुर, 30 अक्टूबर 2026",
            },
        )
        assert res_sim.status_code == 200
        data = res_sim.json()
        assert data["transcript"]["source"] == "preset"
        assert data["draft"]["fields"]["person_name"]["canonical_value"] == "Kamla Devi"
        assert data["draft"]["fields"]["age"]["canonical_value"] == "45"


@pytest.mark.asyncio
async def test_get_languages_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/languages")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) == 11
        codes = [item["code"] for item in data]
        expected_codes = [
            "hi-IN",
            "en-IN",
            "mr-IN",
            "bn-IN",
            "gu-IN",
            "pa-IN",
            "ta-IN",
            "te-IN",
            "kn-IN",
            "ml-IN",
            "or-IN",
        ]
        for c in expected_codes:
            assert c in codes


@pytest.mark.asyncio
async def test_multilingual_draft_lifecycle_and_clarification() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create draft in Tamil
        res_create = await client.post("/api/drafts", data={"language": "ta-IN"})
        assert res_create.status_code == 200
        draft_info = res_create.json()
        draft_id = draft_info["draft_id"]

        res_get = await client.get(f"/api/drafts/{draft_id}")
        assert res_get.status_code == 200
        assert res_get.json()["language"] == "ta-IN"

        # Submit simulated transcript missing age to trigger clarification
        res_sim = await client.post(
            f"/api/drafts/{draft_id}/audio",
            data={
                "expected_version": draft_info["version"],
                "simulated_transcript": "நோயாளி பெயர் கமலா தேவி, கிராமம் ராம்பூர், வருகை தேதி 30 அக்டோபர் 2026",
            },
        )
        assert res_sim.status_code == 200
        data = res_sim.json()
        # Prompt should be localized in Tamil for missing age
        assert data["draft"]["state"] == "NEEDS_CLARIFICATION"
        assert "வயதை" in data["draft"]["active_prompt"]["prompt_text"]


@pytest.mark.asyncio
async def test_cors_preflight_and_origin() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Preflight OPTIONS request from GitHub Pages origin
        headers = {
            "Origin": "https://krishujeniya.github.io",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
        res_options = await client.options("/api/drafts", headers=headers)
        assert res_options.status_code == 200
        assert (
            res_options.headers["access-control-allow-origin"] == "https://krishujeniya.github.io"
        )
        assert "POST" in res_options.headers["access-control-allow-methods"]

        # Simple GET with origin header
        res_get = await client.get("/healthz", headers={"Origin": "https://krishujeniya.github.io"})
        assert res_get.status_code == 200
        assert res_get.headers["access-control-allow-origin"] == "https://krishujeniya.github.io"


@pytest.mark.asyncio
async def test_security_headers_and_cache_control() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # API route must have no-cache headers
        res = await client.get("/api/records")
        assert res.status_code == 200
        assert res.headers["x-content-type-options"] == "nosniff"
        assert res.headers["x-frame-options"] == "DENY"
        assert "no-store" in res.headers["cache-control"]


@pytest.mark.asyncio
async def test_audio_upload_size_limit() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create draft
        res = await client.post("/api/drafts")
        assert res.status_code == 200
        draft_id = res.json()["draft_id"]

        # 11MB dummy payload exceeds 10MB limit
        large_bytes = b"0" * (11 * 1024 * 1024)
        files = {"audio_file": ("large.wav", large_bytes, "audio/wav")}
        data = {"expected_version": 1}

        res_upload = await client.post(f"/api/drafts/{draft_id}/audio", data=data, files=files)
        assert res_upload.status_code == 413
        assert "limit" in res_upload.json()["detail"].lower()


@pytest.mark.asyncio
async def test_root_static_asset_serving() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for asset in [
            "styles.css",
            "design.css",
            "app.js",
            "experience.js",
            "logo.svg",
            "favicon.svg",
        ]:
            res = await client.get(f"/{asset}")
            assert res.status_code == 200, f"Expected 200 for root asset /{asset}"
