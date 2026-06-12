from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_port: int = 8000
    api_host: str = "0.0.0.0"

    db_path: str = "data/studio.db"
    audio_path: str = "data/audio"

    # GPU box model server
    model_server_url: str = "http://localhost:8001"

    # LLM (llama-swap on GPU box) — for translation + note summarization
    llm_url: str = "http://localhost:8080"
    llm_model: str = "qwen3-32k"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
