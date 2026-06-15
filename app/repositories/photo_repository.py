from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.photo import Photo


class PhotoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, photo_id: int) -> Photo | None:
        result = await self.session.execute(select(Photo).where(Photo.id == photo_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Photo]:
        result = await self.session.execute(select(Photo).order_by(Photo.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_tasting(self, tasting_id: int) -> list[Photo]:
        result = await self.session.execute(
            select(Photo).where(Photo.tasting_id == tasting_id).order_by(Photo.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        file_id: str,
        tasting_id: int | None = None,
        description: str | None = None,
    ) -> Photo:
        photo = Photo(file_id=file_id, tasting_id=tasting_id, description=description)
        self.session.add(photo)
        await self.session.commit()
        await self.session.refresh(photo)
        return photo

    async def delete(self, photo_id: int) -> bool:
        photo = await self.get_by_id(photo_id)
        if not photo:
            return False
        await self.session.delete(photo)
        await self.session.commit()
        return True
