from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_port: int = 8000
    api_host: str = "0.0.0.0"

    db_path: str = "data/studio.db"
    audio_path: str = "data/audio"

    # GPU box model server
    model_server_url: str = "http://localhost:8001"

    # ACE-Step API server on GPU box
    acestep_url: str = "http://localhost:8002"

    # LLM (llama-swap on GPU box) — for translation + note summarization
    llm_url: str = "http://localhost:8080"
    # Overridden via LLM_MODEL env (see .env.example). qwen3-32k was the original
    # pick but isn't available on the box; gemma MoE is what actually runs.
    llm_model: str = "gemma-4-26b-a4b-it-mxfp4-moe-ctx-32k-q8-0-kv-t07"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
