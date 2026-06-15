import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from loguru import logger

from app.core.config import settings
from app.core.logger import setup_logger
from app.bot import dp
from app.database.session import init_db
from app.services.scheduler.scheduler_service import get_scheduler


async def main() -> None:
    setup_logger()
    logger.info("Starting Wine Tasting Bot...")

    await init_db()
    logger.info("Database initialized")

    session = None
    if settings.BOT_PROXY:
        logger.info(f"Using proxy: {settings.BOT_PROXY}")
        session = AiohttpSession(proxy=settings.BOT_PROXY)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )

    scheduler = get_scheduler()
    scheduler.start()

    try:
        logger.info("Bot started polling")
        await dp.start_polling(bot)
    finally:
        scheduler.stop()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
