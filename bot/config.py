from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    telegram_token: str
    api_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = BotSettings()
