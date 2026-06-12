import io
import pytest
from unittest.mock import patch, AsyncMock


_FAKE_RESULT = {"text": "hello this is a test", "language": "en", "duration_seconds": 3.5}


@pytest.mark.asyncio
async def test_transcribe_ogg(client):
    with patch("server.routes.transcribe.transcribe", new=AsyncMock(return_value=_FAKE_RESULT)):
        resp = await client.post(
            "/transcribe",
            files={"file": ("voice.ogg", io.BytesIO(b"fake"), "audio/ogg")},
            data={"language": "auto"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["text"] == "hello this is a test"
    assert body["language"] == "en"


@pytest.mark.asyncio
async def test_transcribe_unsupported_format(client):
    with patch("server.routes.transcribe.transcribe", new=AsyncMock(return_value=_FAKE_RESULT)):
        resp = await client.post(
            "/transcribe",
            files={"file": ("video.avi", io.BytesIO(b"fake"), "video/avi")},
        )

    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "unsupported_format"
