import httpx
from server.config import settings


async def transcribe(audio_path: str, language: str = "auto") -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        with open(audio_path, "rb") as f:
            resp = await client.post(
                f"{settings.model_server_url}/whisper",
                files={"file": ("audio", f, "application/octet-stream")},
                data={"language": language},
            )
            resp.raise_for_status()
    return resp.json()
