import asyncio
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from server.config import settings
from server.core.database import init_db
from server.core.job_queue import register_handler, worker
from server.routes import generate, jobs, notes, separate, transcribe, translate


async def _handle_separate(job_id: str, payload: dict) -> dict:
    from server.services.demucs_service import separate as demucs_separate
    return await demucs_separate(payload["audio_path"], job_id)


async def _handle_generate(job_id: str, payload: dict) -> dict:
    from server.services.acestep_service import generate as acestep_generate
    from server.services.llm_service import translate as llm_translate

    lyrics = payload["lyrics"]
    if payload.get("language") == "ru":
        result = await llm_translate(lyrics, "en")
        lyrics = result["text"]

    return await acestep_generate(
        lyrics=lyrics,
        style=payload["style"],
        duration_seconds=payload["duration_seconds"],
        job_id=job_id,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    os.makedirs(settings.audio_path, exist_ok=True)

    register_handler("separate", _handle_separate)
    register_handler("generate", _handle_generate)

    worker_task = asyncio.create_task(worker())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


# data/audio must exist before StaticFiles mounts (happens at import time)
os.makedirs(settings.audio_path, exist_ok=True)

app = FastAPI(title="sona", version="0.1.0", lifespan=lifespan)

app.include_router(transcribe.router)
app.include_router(separate.router)
app.include_router(generate.router)
app.include_router(notes.router)
app.include_router(jobs.router)
app.include_router(translate.router)

app.mount("/audio", StaticFiles(directory=settings.audio_path), name="audio")


@app.get("/health")
async def health():
    gpu_status = {"status": "unreachable"}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.model_server_url}/health")
            gpu_status = resp.json()
    except Exception:
        pass
    return {"status": "ok", "model_server": gpu_status}
