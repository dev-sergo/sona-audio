from pathlib import Path

import httpx

from server.config import settings


async def generate(lyrics: str, style: str, duration_seconds: int, job_id: str) -> dict:
    output_dir = Path(settings.audio_path) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            f"{settings.model_server_url}/acestep",
            data={
                "lyrics": lyrics,
                "style": style,
                "duration_seconds": str(duration_seconds),
            },
        )
        resp.raise_for_status()

    audio_path = output_dir / "output.wav"
    audio_path.write_bytes(resp.content)

    return {"audio": f"/audio/{job_id}/output.wav"}
