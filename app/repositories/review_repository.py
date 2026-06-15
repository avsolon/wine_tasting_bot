from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.review import Review


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, review_id: int) -> Review | None:
        result = await self.session.execute(select(Review).where(Review.id == review_id))
        return result.scalar_one_or_none()

    async def get_active(self) -> list[Review]:
        result = await self.session.execute(
            select(Review).where(Review.is_active == True).order_by(Review.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Review]:
        result = await self.session.execute(select(Review).order_by(Review.created_at.desc()))
        return list(result.scalars().all())

    async def create(
        self,
        author_name: str,
        text: str,
        rating: int | None = None,
        source_url: str | None = None,
    ) -> Review:
        review = Review(
            author_name=author_name,
            text=text,
            rating=rating,
            source_url=source_url,
            is_active=True,
        )
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def update(self, review_id: int, **kwargs) -> Review | None:
        review = await self.get_by_id(review_id)
        if not review:
            return None
        for key, value in kwargs.items():
            if hasattr(review, key):
                setattr(review, key, value)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def delete(self, review_id: int) -> bool:
        review = await self.get_by_id(review_id)
        if not review:
            return False
        await self.session.delete(review)
        await self.session.commit()
        return True
