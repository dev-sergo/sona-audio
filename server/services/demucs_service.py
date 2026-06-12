import io
import zipfile
from pathlib import Path

import httpx

from server.config import settings


async def separate(audio_path: str, job_id: str) -> dict:
    output_dir = Path(settings.audio_path) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=300.0) as client:
        with open(audio_path, "rb") as f:
            resp = await client.post(
                f"{settings.model_server_url}/demucs",
                files={"file": ("audio", f, "application/octet-stream")},
            )
            resp.raise_for_status()

    stems = {}
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for filename in zf.namelist():
            stem_name = filename.replace(".wav", "")
            path = output_dir / filename
            path.write_bytes(zf.read(filename))
            stems[stem_name] = f"/audio/{job_id}/{filename}"

    return stems
