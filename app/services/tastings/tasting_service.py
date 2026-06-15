from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.tasting_repository import TastingRepository
from app.repositories.wine_repository import WineRepository


class TastingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tasting_repo = TastingRepository(session)
        self.wine_repo = WineRepository(session)

    async def get_active_tastings(self):
        return await self.tasting_repo.get_active()

    async def get_tasting_with_wines(self, tasting_id: int):
        tasting = await self.tasting_repo.get_by_id(tasting_id)
        if not tasting:
            return None, []
        wines = await self.wine_repo.get_by_tasting(tasting_id)
        return tasting, wines

    async def close_past_tastings(self) -> int:
        return await self.tasting_repo.close_past_tastings()
