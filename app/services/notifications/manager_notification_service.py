from aiogram import Bot
from loguru import logger
from app.core.config import settings
from app.utils.text_formatter import format_application
from app.database.models.application import Application
from app.database.models.tasting import Tasting


class ManagerNotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.chat_id = settings.MANAGER_CHAT_ID

    async def notify_new_application(self, application: Application, tasting: Tasting) -> bool:
        if not self.chat_id:
            logger.warning("Manager chat ID not configured, skipping notification")
            return False

        text = format_application(application, tasting.title)
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode="Markdown")
            logger.info(f"Manager notified about application #{application.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to notify manager: {e}")
            return False
