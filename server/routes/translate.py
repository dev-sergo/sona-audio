from fastapi import APIRouter
from pydantic import BaseModel

from server.services.llm_service import translate as llm_translate

router = APIRouter()


class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "en"


@router.post("/translate")
async def translate(req: TranslateRequest):
    return await llm_translate(req.text, req.target_lang)
