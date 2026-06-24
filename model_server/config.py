from pydantic_settings import BaseSettings


class ModelServerSettings(BaseSettings):
    port: int = 8001
    host: str = "0.0.0.0"

    whisper_model: str = "large-v3"
    whisper_device: str = "cuda"
    whisper_compute_type: str = "float16"

    # Required for music generation. Set via ACESTEP_MODEL_PATH env / model_server/.env.
    # Use an absolute path — there is no ~ expansion here.
    acestep_model_path: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = ModelServerSettings()
