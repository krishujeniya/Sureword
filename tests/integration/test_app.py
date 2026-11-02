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
