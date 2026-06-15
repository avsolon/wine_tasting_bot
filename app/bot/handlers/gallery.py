from aiogram import Router, types, F
from app.bot.keyboards.main_menu import get_main_menu
from app.database.session import async_session_factory
from app.repositories.photo_repository import PhotoRepository
from app.repositories.review_repository import ReviewRepository
from app.utils.text_formatter import format_review

router = Router()


@router.message(F.text == "📸 Фото и отзывы")
async def show_gallery(message: types.Message) -> None:
    async with async_session_factory() as session:
        photo_repo = PhotoRepository(session)
        review_repo = ReviewRepository(session)
        photos = await photo_repo.get_all()
        reviews = await review_repo.get_active()

    if not photos and not reviews:
        await message.answer("Пока нет фото и отзывов с мероприятий.", reply_markup=get_main_menu())
        return

    await message.answer("📸 *Фото с мероприятий*", parse_mode="Markdown")

    if photos:
        media_group = []
        for photo in photos:
            media_group.append(types.InputMediaPhoto(media=photo.file_id))
            if len(media_group) == 10:
                await message.answer_media_group(media=media_group)
                media_group = []
        if media_group:
            await message.answer_media_group(media=media_group)
    else:
        await message.answer("Пока нет фотографий.")

    if reviews:
        await message.answer("⭐ *Отзывы участников:*", parse_mode="Markdown")
        for review in reviews:
            text = format_review(review)
            await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

    await message.answer("Главное меню:", reply_markup=get_main_menu())
