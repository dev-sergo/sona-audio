from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.core.job_queue import enqueue

router = APIRouter()


class GenerateRequest(BaseModel):
    lyrics: str
    style: str = "pop"
    language: str = "en"
    duration_seconds: int = 30


@router.post("/generate")
async def generate_music(req: GenerateRequest):
    if not req.lyrics.strip():
        raise HTTPException(
            400,
            detail={"error": "empty_lyrics", "message": "Lyrics cannot be empty"},
        )
    if not 15 <= req.duration_seconds <= 120:
        raise HTTPException(
            400,
            detail={"error": "invalid_duration", "message": "duration_seconds must be 15–120"},
        )

    job_id = await enqueue("generate", req.model_dump())
    return {"job_id": job_id}
