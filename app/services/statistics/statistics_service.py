from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.tasting_repository import TastingRepository
from app.repositories.application_repository import ApplicationRepository


class StatisticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tasting_repo = TastingRepository(session)
        self.application_repo = ApplicationRepository(session)

    async def get_statistics(self) -> dict:
        tastings = await self.tasting_repo.get_all()
        total_tastings = len(tastings)
        total_applications = await self.application_repo.get_total_count()
        total_guests = await self.application_repo.get_total_guests()

        total_seats = sum(t.total_seats for t in tastings)
        total_booked = sum(t.total_seats - t.available_seats for t in tastings if t.status == "active")
        avg_fill = (total_booked / total_seats * 100) if total_seats > 0 else 0.0

        active_tastings = [t for t in tastings if t.status == "active"]
        next_event = min(active_tastings, key=lambda t: t.date).title if active_tastings else None

        return {
            "total_tastings": total_tastings,
            "total_applications": total_applications,
            "total_guests": total_guests,
            "avg_fill": avg_fill,
            "next_event": next_event,
        }
