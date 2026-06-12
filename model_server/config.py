from pydantic_settings import BaseSettings


class ModelServerSettings(BaseSettings):
    port: int = 8001
    host: str = "0.0.0.0"

    whisper_model: str = "large-v3"
    whisper_device: str = "cuda"
    whisper_compute_type: str = "float16"

    acestep_model_path: str = "/home/serbio/Documents/ComfyUI/models/ace-step"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = ModelServerSettings()
