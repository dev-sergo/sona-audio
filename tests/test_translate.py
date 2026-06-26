import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_translate_ru_to_en(client):
    fake = AsyncMock(return_value={"text": "hello world", "target_lang": "en"})
    with patch("server.routes.translate.llm_translate", new=fake):
        resp = await client.post("/translate", json={"text": "hola mundo", "target_lang": "en"})

    assert resp.status_code == 200
    assert resp.json()["text"] == "hello world"


@pytest.mark.asyncio
async def test_translate_missing_fields(client):
    # 'text' is required; 'target_lang' defaults to "en". Omitting 'text' must fail
    # schema validation (422) before the route ever calls the LLM.
    resp = await client.post("/translate", json={"target_lang": "en"})
    assert resp.status_code == 422
