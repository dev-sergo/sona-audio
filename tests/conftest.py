import os
import tempfile

# Must run before any server.* import — pydantic-settings reads env at class instantiation
_tmpdir = tempfile.mkdtemp(prefix="alf_test_")
os.environ.setdefault("DB_PATH", os.path.join(_tmpdir, "test.db"))
os.environ.setdefault("AUDIO_PATH", os.path.join(_tmpdir, "audio"))
os.environ.setdefault("MODEL_SERVER_URL", "http://fake-model:8001")
os.environ.setdefault("LLM_URL", "http://fake-llm:8080")
os.environ.setdefault("LLM_MODEL", "test-model")
os.environ.setdefault("TELEGRAM_TOKEN", "0:test")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport


@pytest_asyncio.fixture
async def client():
    from server.core.database import init_db
    await init_db()
    from server.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
