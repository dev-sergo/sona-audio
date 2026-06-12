import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_health_ok(client):
    with patch("server.main.httpx.AsyncClient") as mock_cls:
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http.get = AsyncMock(return_value=AsyncMock(json=lambda: {"status": "ok"}))
        mock_cls.return_value = mock_http

        resp = await client.get("/health")

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
