import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_job_not_found(client):
    resp = await client.get("/jobs/gen_doesnotexist")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_separate_enqueues_job(client):
    import io
    fake_wav = b"RIFF\x00\x00\x00\x00WAVEfmt "

    with patch("server.routes.separate.enqueue", new=AsyncMock(return_value="sep_abc123")):
        resp = await client.post(
            "/separate",
            files={"file": ("track.mp3", io.BytesIO(fake_wav), "audio/mpeg")},
        )

    assert resp.status_code == 200
    assert resp.json()["job_id"] == "sep_abc123"


@pytest.mark.asyncio
async def test_generate_enqueues_job(client):
    with patch("server.routes.generate.enqueue", new=AsyncMock(return_value="gen_xyz789")):
        resp = await client.post("/generate", json={
            "lyrics": "verse one bars",
            "style": "hip-hop, dark",
            "language": "en",
            "duration_seconds": 30,
        })

    assert resp.status_code == 200
    assert resp.json()["job_id"] == "gen_xyz789"
