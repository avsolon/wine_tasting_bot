from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.repositories.application_repository import ApplicationRepository
from app.repositories.tasting_repository import TastingRepository
from app.repositories.user_repository import UserRepository
from app.services.bitrix24.lead_service import Bitrix24LeadService
from app.services.notifications.manager_notification_service import ManagerNotificationService
from app.database.models.application import Application
from aiogram import Bot


class RegistrationService:
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot
        self.application_repo = ApplicationRepository(session)
        self.tasting_repo = TastingRepository(session)
        self.user_repo = UserRepository(session)
        self.bitrix24 = Bitrix24LeadService()
        self.manager_notifier = ManagerNotificationService(bot)

    async def register(
        self,
        tasting_id: int,
        telegram_id: int,
        name: str,
        phone: str,
        guests_count: int = 1,
        comment: str | None = None,
    ) -> tuple[Application | None, str | None]:
        tasting = await self.tasting_repo.get_by_id(tasting_id)
        if not tasting:
            return None, "Дегустация не найдена."

        if tasting.status != "active":
            return None, "Эта дегустация уже завершена."

        if tasting.available_seats < guests_count:
            return None, "К сожалению, свободных мест недостаточно."

        existing = await self.application_repo.get_user_application_for_tasting(telegram_id, tasting_id)
        if existing:
            return None, "Вы уже зарегистрированы на данную дегустацию."

        application = await self.application_repo.create(
            tasting_id=tasting_id,
            telegram_id=telegram_id,
            name=name,
            phone=phone,
            guests_count=guests_count,
            comment=comment,
        )

        tasting.available_seats -= guests_count
        await self.session.commit()

        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user:
            if not user.phone:
                await self.user_repo.update_phone(telegram_id, phone)
            if not user.full_name:
                await self.user_repo.update_full_name(telegram_id, name)

        crm_lead_id = await self.bitrix24.create_lead(
            name=name,
            phone=phone,
            comment=f"{guests_count} гостя. {comment or ''}".strip(),
            event_name=tasting.title,
            telegram_id=telegram_id,
            price=tasting.price,
            guests_count=guests_count,
        )
        if crm_lead_id:
            await self.application_repo.update_crm_lead(application.id, crm_lead_id)

        await self.manager_notifier.notify_new_application(application, tasting)

        return application, None
