from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    PROJECT_NAME: str = "Aniks"
    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",
    ]

    LOCAL_DEV: bool = False
    PROD_DOMAIN: str | None = None
    API_KEYS: list[str]

    def model_post_init(self, __context):
        if self.PROD_DOMAIN and not self.LOCAL_DEV:
            self.CORS_ALLOWED_ORIGINS.append(self.PROD_DOMAIN)
        if self.LOCAL_DEV:
            self.API_KEYS.append("test_key")

    # LLM
    GEMINI_API_KEY: str

    # Telegrams
    AP_ID: str
    API_HASH: str
    SESSION_STRING: str
    APP_TITLE: str
    SHORT_NAME: str

    # Telegram chat digest
    CHAT_DIGEST_CHAT_NAME_PREFIX: str | None = None
    CHAT_DIGEST_TOPICS: str = ""
    CHAT_DIGEST_EXTRA_INSTRUCTIONS: str = ""

    # Alert-in-ua api key
    ALERTS_TOKEN: str | None = None


settings = Settings()
