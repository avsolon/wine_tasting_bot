from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.application import Application


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, application_id: int) -> Application | None:
        result = await self.session.execute(select(Application).where(Application.id == application_id))
        return result.scalar_one_or_none()

    async def get_by_tasting(self, tasting_id: int) -> list[Application]:
        result = await self.session.execute(
            select(Application).where(Application.tasting_id == tasting_id).order_by(Application.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Application]:
        result = await self.session.execute(select(Application).order_by(Application.created_at.desc()))
        return list(result.scalars().all())

    async def get_user_application_for_tasting(self, telegram_id: int, tasting_id: int) -> Application | None:
        result = await self.session.execute(
            select(Application).where(
                and_(
                    Application.telegram_id == telegram_id,
                    Application.tasting_id == tasting_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        tasting_id: int,
        telegram_id: int,
        name: str,
        phone: str,
        guests_count: int = 1,
        comment: str | None = None,
    ) -> Application:
        application = Application(
            tasting_id=tasting_id,
            telegram_id=telegram_id,
            name=name,
            phone=phone,
            guests_count=guests_count,
            comment=comment,
            status="pending",
        )
        self.session.add(application)
        await self.session.commit()
        await self.session.refresh(application)
        return application

    async def update_crm_lead(self, application_id: int, crm_lead_id: str) -> Application | None:
        application = await self.get_by_id(application_id)
        if application:
            application.crm_lead_id = crm_lead_id
            await self.session.commit()
            await self.session.refresh(application)
        return application

    async def update_status(self, application_id: int, status: str) -> Application | None:
        application = await self.get_by_id(application_id)
        if application:
            application.status = status
            await self.session.commit()
            await self.session.refresh(application)
        return application

    async def get_total_count(self) -> int:
        result = await self.session.execute(select(Application))
        return len(result.scalars().all())

    async def get_total_guests(self) -> int:
        result = await self.session.execute(select(Application))
        applications = result.scalars().all()
        return sum(a.guests_count for a in applications)
