from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.tasting import Tasting


class TastingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, tasting_id: int) -> Tasting | None:
        result = await self.session.execute(select(Tasting).where(Tasting.id == tasting_id))
        return result.scalar_one_or_none()

    async def get_active(self) -> list[Tasting]:
        result = await self.session.execute(
            select(Tasting).where(Tasting.status == "active").order_by(Tasting.date)
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Tasting]:
        result = await self.session.execute(select(Tasting).order_by(Tasting.date.desc()))
        return list(result.scalars().all())

    async def create(
        self,
        title: str,
        date: str,
        time: str,
        price: float,
        total_seats: int,
        description: str,
    ) -> Tasting:
        tasting = Tasting(
            title=title,
            date=date,
            time=time,
            price=price,
            total_seats=total_seats,
            available_seats=total_seats,
            description=description,
            status="active",
        )
        self.session.add(tasting)
        await self.session.commit()
        await self.session.refresh(tasting)
        return tasting

    async def update(self, tasting_id: int, **kwargs) -> Tasting | None:
        tasting = await self.get_by_id(tasting_id)
        if not tasting:
            return None
        for key, value in kwargs.items():
            if hasattr(tasting, key):
                setattr(tasting, key, value)
        await self.session.commit()
        await self.session.refresh(tasting)
        return tasting

    async def delete(self, tasting_id: int) -> bool:
        tasting = await self.get_by_id(tasting_id)
        if not tasting:
            return False
        await self.session.delete(tasting)
        await self.session.commit()
        return True

    async def close_past_tastings(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        result = await self.session.execute(
            update(Tasting)
            .where(Tasting.status == "active")
            .where(Tasting.date < today)
            .values(status="finished")
        )
        await self.session.commit()
        return result.rowcount
