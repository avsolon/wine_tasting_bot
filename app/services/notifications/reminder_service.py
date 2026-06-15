from aiogram import Bot
from loguru import logger
from app.core.constants import REMINDER_24H_TEXT, REMINDER_1H_TEXT
from app.database.models.tasting import Tasting
from app.utils.text_formatter import format_tasting


class ReminderService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_tasting_info(self, telegram_id: int, tasting: Tasting) -> bool:
        text = (
            "✅ *Вы записаны!*\n\n"
            f"{format_tasting(tasting)}\n\n"
            "Мы получили вашу заявку и вскоре наш менеджер свяжется с вами."
        )
        try:
            await self.bot.send_message(chat_id=telegram_id, text=text, parse_mode="Markdown")
            logger.info(f"Tasting info sent to {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send tasting info to {telegram_id}: {e}")
            return False

    async def send_reminder_24h(self, telegram_id: int, tasting_title: str) -> bool:
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=f"{REMINDER_24H_TEXT}\n\n🍷 *{tasting_title}*",
                parse_mode="Markdown",
            )
            logger.info(f"24h reminder sent to {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send 24h reminder to {telegram_id}: {e}")
            return False

    async def send_reminder_1h(self, telegram_id: int, tasting_title: str) -> bool:
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=f"{REMINDER_1H_TEXT}\n\n🍷 *{tasting_title}*",
                parse_mode="Markdown",
            )
            logger.info(f"1h reminder sent to {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send 1h reminder to {telegram_id}: {e}")
            return False

    async def send_review_reminder(self, telegram_id: int, tasting_title: str) -> bool:
        text = (
            "Спасибо за участие в дегустации! 🍷\n\n"
            "Будем благодарны, если вы оставите отзыв о мероприятии.\n\n"
            "Оставить отзыв можно по ссылке ниже:\n"
            "https://example.com/review"
        )
        try:
            await self.bot.send_message(chat_id=telegram_id, text=text, parse_mode="Markdown")
            logger.info(f"Review reminder sent to {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send review reminder to {telegram_id}: {e}")
            return False
