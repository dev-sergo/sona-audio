import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Callable, Awaitable

import aiosqlite

from server.config import settings

_queue: asyncio.Queue = asyncio.Queue()
_handlers: dict[str, Callable[[str, dict], Awaitable[dict]]] = {}


def register_handler(job_type: str, fn: Callable[[str, dict], Awaitable[dict]]):
    _handlers[job_type] = fn


async def enqueue(job_type: str, payload: dict) -> str:
    job_id = f"{job_type[:3]}_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "INSERT INTO jobs (id, type, status, created_at, updated_at) VALUES (?, ?, 'pending', ?, ?)",
            (job_id, job_type, now, now),
        )
        await db.commit()
    await _queue.put((job_id, job_type, payload))
    return job_id


async def get_job(job_id: str) -> dict | None:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)) as cur:
            row = await cur.fetchone()
    if row is None:
        return None
    d = dict(row)
    if d["result"]:
        d["result"] = json.loads(d["result"])
    return d


async def _update_job(
    job_id: str,
    status: str,
    result: dict | None = None,
    error: str | None = None,
    progress: float = 0.0,
):
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "UPDATE jobs SET status=?, result=?, error=?, progress=?, updated_at=? WHERE id=?",
            (status, json.dumps(result) if result else None, error, progress, now, job_id),
        )
        await db.commit()


async def worker():
    while True:
        job_id, job_type, payload = await _queue.get()
        await _update_job(job_id, "running")
        handler = _handlers.get(job_type)
        if handler is None:
            await _update_job(job_id, "error", error=f"no handler for job type '{job_type}'")
            _queue.task_done()
            continue
        try:
            result = await handler(job_id, payload)
            await _update_job(job_id, "done", result=result, progress=1.0)
        except Exception as e:
            await _update_job(job_id, "error", error=str(e))
        finally:
            _queue.task_done()
