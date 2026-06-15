from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.wine import Wine


class WineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, wine_id: int) -> Wine | None:
        result = await self.session.execute(select(Wine).where(Wine.id == wine_id))
        return result.scalar_one_or_none()

    async def get_by_tasting(self, tasting_id: int) -> list[Wine]:
        result = await self.session.execute(
            select(Wine).where(Wine.tasting_id == tasting_id).order_by(Wine.id)
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Wine]:
        result = await self.session.execute(select(Wine).order_by(Wine.id))
        return list(result.scalars().all())

    async def create(
        self,
        tasting_id: int,
        name: str,
        country: str | None = None,
        region: str | None = None,
        grape: str | None = None,
        description: str | None = None,
        photo_file_id: str | None = None,
    ) -> Wine:
        wine = Wine(
            tasting_id=tasting_id,
            name=name,
            country=country,
            region=region,
            grape=grape,
            description=description,
            photo_file_id=photo_file_id,
        )
        self.session.add(wine)
        await self.session.commit()
        await self.session.refresh(wine)
        return wine

    async def update(self, wine_id: int, **kwargs) -> Wine | None:
        wine = await self.get_by_id(wine_id)
        if not wine:
            return None
        for key, value in kwargs.items():
            if hasattr(wine, key):
                setattr(wine, key, value)
        await self.session.commit()
        await self.session.refresh(wine)
        return wine

    async def delete(self, wine_id: int) -> bool:
        wine = await self.get_by_id(wine_id)
        if not wine:
            return False
        await self.session.delete(wine)
        await self.session.commit()
        return True
