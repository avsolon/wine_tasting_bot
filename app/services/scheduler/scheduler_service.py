from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from loguru import logger


_scheduler_instance: "SchedulerService | None" = None


def get_scheduler() -> "SchedulerService":
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SchedulerService()
    return _scheduler_instance


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.add_job(
            self.close_past_tastings_job,
            CronTrigger(hour=0, minute=0),
            id="close_past_tastings",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("Scheduler started")

    async def close_past_tastings_job(self) -> None:
        from app.database.session import async_session_factory
        from app.services.tastings.tasting_service import TastingService

        async with async_session_factory() as session:
            service = TastingService(session)
            count = await service.close_past_tastings()
            if count:
                logger.info(f"Closed {count} past tastings")

    def schedule_reminders(
        self,
        telegram_id: int,
        tasting_title: str,
        date_str: str,
        time_str: str,
    ) -> None:
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            now = datetime.now()

            reminder_24h = dt - timedelta(hours=24)
            if reminder_24h > now:
                self.scheduler.add_job(
                    self._send_reminder_24h,
                    trigger=DateTrigger(run_date=reminder_24h),
                    args=[telegram_id, tasting_title],
                    id=f"reminder_24h_{telegram_id}_{tasting_title[:20]}",
                    replace_existing=True,
                )
                logger.info(f"24h reminder scheduled for {reminder_24h}")

            reminder_1h = dt - timedelta(hours=1)
            if reminder_1h > now:
                self.scheduler.add_job(
                    self._send_reminder_1h,
                    trigger=DateTrigger(run_date=reminder_1h),
                    args=[telegram_id, tasting_title],
                    id=f"reminder_1h_{telegram_id}_{tasting_title[:20]}",
                    replace_existing=True,
                )
                logger.info(f"1h reminder scheduled for {reminder_1h}")

        except Exception as e:
            logger.error(f"Failed to schedule reminders: {e}")

    async def _send_reminder_24h(self, telegram_id: int, tasting_title: str) -> None:
        from app.database.session import async_session_factory
        from app.services.notifications.reminder_service import ReminderService
        from aiogram import Bot
        from app.core.config import settings

        bot = Bot(token=settings.BOT_TOKEN)
        service = ReminderService(bot)
        await service.send_reminder_24h(telegram_id, tasting_title)
        await bot.session.close()

    async def _send_reminder_1h(self, telegram_id: int, tasting_title: str) -> None:
        from app.database.session import async_session_factory
        from app.services.notifications.reminder_service import ReminderService
        from aiogram import Bot
        from app.core.config import settings

        bot = Bot(token=settings.BOT_TOKEN)
        service = ReminderService(bot)
        await service.send_reminder_1h(telegram_id, tasting_title)
        await bot.session.close()

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()
