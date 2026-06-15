from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.bot.keyboards.main_menu import get_main_menu
from app.bot.keyboards.tasting_menu import (
    get_tastings_keyboard,
    get_tasting_detail_keyboard,
    get_tasting_selection_keyboard,
)
from app.database.session import async_session_factory
from app.repositories.tasting_repository import TastingRepository
from app.utils.text_formatter import format_tasting

router = Router()


@router.message(F.text == "🍷 Предстоящие дегустации")
async def show_tastings(message: types.Message) -> None:
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tastings = await repo.get_active()

    if not tastings:
        await message.answer("🍷 На данный момент нет предстоящих дегустаций.", reply_markup=get_main_menu())
        return

    await message.answer("🍷 *Предстоящие дегустации*", parse_mode="Markdown")
    await message.answer(
        "Выберите дегустацию для подробной информации:",
        reply_markup=get_tastings_keyboard(tastings),
    )


@router.callback_query(F.data.startswith("tasting_view:"))
async def tasting_detail(callback: types.CallbackQuery) -> None:
    tasting_id = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tasting = await repo.get_by_id(tasting_id)

    if not tasting:
        await callback.message.edit_text("Дегустация не найдена.")
        return

    text = format_tasting(tasting)
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_tasting_detail_keyboard(tasting_id),
    )
    await callback.answer()


@router.callback_query(F.data == "tastings_back")
async def tastings_back(callback: types.CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=get_main_menu())
    await callback.answer()
