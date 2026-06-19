import asyncio
from functools import lru_cache

_MODEL_NAME = "Helsinki-NLP/opus-mt-ru-en"


@lru_cache(maxsize=1)
def _load_model():
    from transformers import MarianMTModel, MarianTokenizer
    tokenizer = MarianTokenizer.from_pretrained(_MODEL_NAME)
    model = MarianMTModel.from_pretrained(_MODEL_NAME)
    return tokenizer, model


async def translate_ru_en(text: str) -> str:
    loop = asyncio.get_event_loop()

    def _translate():
        tokenizer, model = _load_model()
        inputs = tokenizer([text], return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated = model.generate(**inputs)
        return tokenizer.decode(translated[0], skip_special_tokens=True)

    return await loop.run_in_executor(None, _translate)
