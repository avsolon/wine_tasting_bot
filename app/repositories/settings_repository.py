from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.settings import Settings


class SettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, key: str) -> str | None:
        result = await self.session.execute(select(Settings).where(Settings.key == key))
        setting = result.scalar_one_or_none()
        return setting.value if setting else None

    async def set(self, key: str, value: str) -> None:
        result = await self.session.execute(select(Settings).where(Settings.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            self.session.add(Settings(key=key, value=value))
        await self.session.commit()

    async def get_all(self) -> dict[str, str]:
        result = await self.session.execute(select(Settings))
        settings = result.scalars().all()
        return {s.key: s.value for s in settings}
