import json
import re

import httpx

from server.config import settings

_LANG_NAMES = {"en": "English", "ru": "Russian"}


async def translate(text: str, target_lang: str) -> dict:
    lang_name = _LANG_NAMES.get(target_lang, target_lang)
    prompt = (
        f"Translate the following text to {lang_name}. "
        f"Output only the translation, nothing else.\n\n{text}"
    )
    content = await _chat(prompt, max_tokens=2000, temperature=0.1)
    return {"text": content.strip(), "target_lang": target_lang}


async def summarize_note(text: str) -> dict:
    prompt = (
        'Analyze this text and return a JSON object with keys:\n'
        '"title" (5-10 words), "summary" (2-3 sentences), "tags" (list of 3-5 strings).\n'
        "Respond with valid JSON only, no extra text.\n\n"
        f"Text: {text}"
    )
    content = await _chat(prompt, max_tokens=500, temperature=0.3)
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"title": text[:60].strip(), "summary": "", "tags": []}


async def _chat(prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.llm_url}/v1/chat/completions",
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
