from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    BOT_TOKEN: str
    ADMIN_IDS: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/db/wine_club.db"
    BITRIX24_WEBHOOK_URL: str = ""
    MANAGER_CHAT_ID: int = 0
    LOG_LEVEL: str = "DEBUG"
    BOT_PROXY: str = ""

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]


settings = Settings()
