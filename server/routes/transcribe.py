import os
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from server.services.whisper_service import transcribe

router = APIRouter()

_SUPPORTED = {".ogg", ".mp3", ".wav", ".m4a", ".flac", ".opus"}


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(default="auto"),
):
    ext = os.path.splitext(file.filename or "audio")[1].lower() or ".ogg"
    if ext not in _SUPPORTED:
        raise HTTPException(
            400,
            detail={"error": "unsupported_format", "message": f"Supported formats: {_SUPPORTED}"},
        )

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = await transcribe(tmp_path, language=language)
    finally:
        os.unlink(tmp_path)

    return result
