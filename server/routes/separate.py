import os
import uuid

from fastapi import APIRouter, File, UploadFile

from server.config import settings
from server.core.job_queue import enqueue

router = APIRouter()


@router.post("/separate")
async def separate_audio(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "audio")[1].lower() or ".mp3"

    upload_dir = os.path.join(settings.audio_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    upload_path = os.path.join(upload_dir, f"{uuid.uuid4().hex[:8]}{ext}")
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    job_id = await enqueue("separate", {"audio_path": upload_path})
    return {"job_id": job_id}
