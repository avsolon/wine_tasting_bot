from aiogram import Router, types, F
from app.bot.keyboards.main_menu import get_main_menu
from app.bot.keyboards.tasting_menu import get_wine_tastings_keyboard
from app.database.session import async_session_factory
from app.repositories.tasting_repository import TastingRepository
from app.repositories.wine_repository import WineRepository
from app.utils.text_formatter import format_wine

router = Router()


@router.message(F.text == "🍇 Коллекция вин")
async def show_wines(message: types.Message) -> None:
    async with async_session_factory() as session:
        tasting_repo = TastingRepository(session)
        tastings = await tasting_repo.get_active()

    if not tastings:
        await message.answer("На данный нет активных дегустаций с подборкой вин.", reply_markup=get_main_menu())
        return

    await message.answer(
        "Выберите дегустацию, чтобы увидеть вина в подборке:",
        reply_markup=get_wine_tastings_keyboard(tastings),
    )


@router.callback_query(F.data.startswith("wine_tasting:"))
async def show_wines_for_tasting(callback: types.CallbackQuery) -> None:
    tasting_id = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        wine_repo = WineRepository(session)
        tasting_repo = TastingRepository(session)
        wines = await wine_repo.get_by_tasting(tasting_id)
        tasting = await tasting_repo.get_by_id(tasting_id)

    if not tasting:
        await callback.message.edit_text("Дегустация не найдена.")
        await callback.answer()
        return

    if not wines:
        await callback.message.edit_text(
            f"Для дегустации «{tasting.title}» пока нет добавленных вин.",
            reply_markup=get_main_menu(),
        )
        await callback.answer()
        return

    await callback.message.delete()
    for wine in wines:
        text = format_wine(wine)
        if wine.photo_file_id:
            await callback.message.answer_photo(
                photo=wine.photo_file_id,
                caption=text,
                parse_mode="Markdown",
            )
        else:
            await callback.message.answer(text, parse_mode="Markdown")

    await callback.message.answer("Главное меню:", reply_markup=get_main_menu())
    await callback.answer()
