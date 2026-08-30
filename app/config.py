from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ""
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"
    bot_mode: str = "polling"
    webapp_url: str = "http://127.0.0.1:8000"
    webhook_url: str = ""
    webhook_secret: str = ""
    webhook_path: str = "/telegram/webhook"
    max_history: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def webhook_enabled(self) -> bool:
        return self.bot_mode == "webhook" and bool(self.webhook_url) and bool(self.bot_token)

    @property
    def polling_enabled(self) -> bool:
        return bool(self.bot_token) and not self.webhook_enabled

    @property
    def webapp_is_https(self) -> bool:
        return self.webapp_url.startswith("https://")


settings = Settings()
