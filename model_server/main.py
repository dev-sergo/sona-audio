import asyncio
import io
import os
import tempfile
import zipfile
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from model_server.config import settings

_models: dict = {}


# ── model loaders (run in thread pool, blocking) ────────────────────────────

def _load_whisper():
    from faster_whisper import WhisperModel
    print("Loading Whisper...")
    model = WhisperModel(
        settings.whisper_model,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
    )
    print("Whisper ready.")
    return model


def _load_demucs():
    from demucs.pretrained import get_model
    print("Loading Demucs...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = get_model("htdemucs")
    model.to(device)
    model.eval()
    print("Demucs ready.")
    return model


# ── app lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    _models["whisper"] = await loop.run_in_executor(None, _load_whisper)
    _models["demucs"] = await loop.run_in_executor(None, _load_demucs)
    yield
    _models.clear()


app = FastAPI(title="sona model-server", lifespan=lifespan)


# ── health ───────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    free, total = (0, 0)
    if torch.cuda.is_available():
        free, total = torch.cuda.mem_get_info()
    return {
        "status": "ok",
        "models_loaded": list(_models.keys()),
        "vram_free_gb": round(free / 1024 ** 3, 2),
        "vram_total_gb": round(total / 1024 ** 3, 2),
    }


# ── whisper ──────────────────────────────────────────────────────────────────

@app.post("/whisper")
async def whisper_transcribe(
    file: UploadFile = File(...),
    language: str = Form(default="auto"),
):
    ext = os.path.splitext(file.filename or "audio")[1] or ".ogg"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        def _run():
            model = _models["whisper"]
            segments, info = model.transcribe(
                tmp_path,
                language=language if language != "auto" else None,
                beam_size=5,
            )
            text = " ".join(s.text.strip() for s in segments)
            return {
                "text": text,
                "language": info.language,
                "duration_seconds": round(info.duration, 2),
            }

        result = await asyncio.get_event_loop().run_in_executor(None, _run)
    finally:
        os.unlink(tmp_path)

    return result


# ── demucs ───────────────────────────────────────────────────────────────────

@app.post("/demucs")
async def demucs_separate(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "audio")[1] or ".mp3"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        def _run():
            import torchaudio
            import torchaudio.functional as F
            from demucs.apply import apply_model

            model = _models["demucs"]
            device = next(model.parameters()).device

            wav, sr = torchaudio.load(tmp_path)
            if sr != model.samplerate:
                wav = F.resample(wav, sr, model.samplerate)
            if wav.shape[0] == 1:
                wav = wav.repeat(model.audio_channels, 1)
            elif wav.shape[0] > model.audio_channels:
                wav = wav[: model.audio_channels]

            with torch.no_grad():
                sources = apply_model(model, wav.unsqueeze(0).to(device))[0]

            stems = {}
            with tempfile.TemporaryDirectory() as tmpdir:
                for i, name in enumerate(model.sources):
                    path = os.path.join(tmpdir, f"{name}.wav")
                    torchaudio.save(path, sources[i].cpu(), model.samplerate)
                    with open(path, "rb") as f:
                        stems[name] = f.read()
            return stems

        stems = await asyncio.get_event_loop().run_in_executor(None, _run)
    finally:
        os.unlink(tmp_path)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in stems.items():
            zf.writestr(f"{name}.wav", data)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=stems.zip"},
    )


# ── acestep (stub) ───────────────────────────────────────────────────────────

@app.post("/acestep")
async def acestep_generate(
    lyrics: str = Form(...),
    style: str = Form(default="pop"),
    duration_seconds: int = Form(default=30),
):
    # TODO: implement after verifying ACE-Step Python API
    # Weights: settings.acestep_model_path
    # Reference: ~/Documents/ComfyUI/custom_nodes/ACE-Step-1.5/
    raise HTTPException(
        501,
        detail={"error": "not_implemented", "message": "ACE-Step not implemented yet"},
    )
