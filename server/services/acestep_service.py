import asyncio
import json
from pathlib import Path

import httpx

from server.config import settings

_POLL_INTERVAL = 5      # seconds between status checks
_POLL_MAX = 120         # 120 × 5s = 10 minutes max

# Status codes from ACE-Step query_result:
# 0 = queued/running, 1 = succeeded, 2 = failed/timeout


async def generate(lyrics: str, style: str, duration_seconds: int, job_id: str) -> dict:
    output_dir = Path(settings.audio_path) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    base = settings.acestep_url

    # 1. Submit task
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{base}/release_task",
            json={
                "prompt": style,
                "lyrics": lyrics,
                "audio_duration": float(duration_seconds),
                "vocal_language": "en",
                "task_type": "text2music",
                "thinking": False,
                "lm_backend": "pt",
                "inference_steps": 20,
                "guidance_scale": 7.0,
                "audio_format": "wav",
                "use_random_seed": True,
            },
        )
        resp.raise_for_status()
        task_id = resp.json()["data"]["task_id"]

    # 2. Poll until done
    for _ in range(_POLL_MAX):
        await asyncio.sleep(_POLL_INTERVAL)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{base}/query_result",
                    json={"task_id_list": [task_id]},
                )
                resp.raise_for_status()
                items = resp.json().get("data", [])
        except httpx.TimeoutException:
            continue  # GPU busy (e.g. model loading), retry next poll

        if not items:
            continue

        item = items[0]
        status = item.get("status")  # int: 0=running, 1=succeeded, 2=failed

        if status == 2:
            result_str = item.get("result", "[]")
            result_items = json.loads(result_str) if isinstance(result_str, str) else result_str
            error = result_items[0].get("error") if result_items else None
            raise RuntimeError(error or "ACE-Step generation failed")

        if status == 1:
            result_str = item.get("result", "[]")
            result_items = json.loads(result_str) if isinstance(result_str, str) else result_str
            if not result_items:
                raise RuntimeError("No audio data in ACE-Step result")
            audio_path = result_items[0].get("file", "")
            if not audio_path:
                raise RuntimeError(f"No audio file path in result: {result_items}")

            # 3. Download and save locally
            # file may already be a URL path like /v1/audio?path=... or a raw fs path
            if audio_path.startswith("http"):
                download_url = audio_path
            elif audio_path.startswith("/v1/audio"):
                download_url = f"{base}{audio_path}"
            else:
                download_url = f"{base}/v1/audio?path={audio_path}"
            async with httpx.AsyncClient(timeout=120.0) as client:
                dl = await client.get(download_url)
                dl.raise_for_status()

            out = output_dir / "output.wav"
            out.write_bytes(dl.content)

            return {"audio": f"/audio/{job_id}/output.wav", "task_id": task_id}

    raise TimeoutError("ACE-Step generation timed out after 10 minutes")
