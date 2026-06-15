from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, username: str | None = None, full_name: str | None = None) -> User:
        user = User(telegram_id=telegram_id, username=username, full_name=full_name)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_phone(self, telegram_id: int, phone: str) -> User | None:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.phone = phone
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def update_full_name(self, telegram_id: int, full_name: str) -> User | None:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.full_name = full_name
            await self.session.commit()
            await self.session.refresh(user)
        return user
