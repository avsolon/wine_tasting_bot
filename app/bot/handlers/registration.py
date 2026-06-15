from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.core.constants import REGISTRATION_CONFIRMATION
from app.bot.keyboards.main_menu import get_main_menu
from app.bot.keyboards.tasting_menu import get_tasting_selection_keyboard
from app.bot.keyboards.registration import get_confirm_keyboard, get_cancel_keyboard
from app.bot.states.registration import RegistrationStates
from app.database.session import async_session_factory
from app.repositories.tasting_repository import TastingRepository
from app.services.registrations.registration_service import RegistrationService
from app.services.notifications.reminder_service import ReminderService
from app.services.scheduler.scheduler_service import get_scheduler
from app.utils.phone_validator import validate_phone
from app.utils.text_formatter import format_tasting
from aiogram import Bot

router = Router()


@router.message(F.text == "📝 Записаться")
async def start_registration(message: types.Message, state: FSMContext) -> None:
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tastings = await repo.get_active()

    if not tastings:
        await message.answer("На данный момент нет активных дегустаций для записи.", reply_markup=get_main_menu())
        return

    await state.set_state(RegistrationStates.select_tasting)
    await message.answer(
        "Выберите дегустацию:",
        reply_markup=get_tasting_selection_keyboard(tastings),
    )


@router.callback_query(F.data.startswith("register_select:"))
async def select_tasting(callback: types.CallbackQuery, state: FSMContext) -> None:
    tasting_id = int(callback.data.split(":")[1])
    await state.update_data(tasting_id=tasting_id)
    await state.set_state(RegistrationStates.input_name)
    await callback.message.edit_text("Введите ваше имя:")
    await callback.answer()


@router.callback_query(F.data.startswith("tasting_register:"))
async def register_from_tasting_card(callback: types.CallbackQuery, state: FSMContext) -> None:
    tasting_id = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tasting = await repo.get_by_id(tasting_id)
    if not tasting or tasting.status != "active":
        await callback.answer("Эта дегустация недоступна для записи.", show_alert=True)
        return
    await state.update_data(tasting_id=tasting_id)
    await state.set_state(RegistrationStates.input_name)
    await callback.message.edit_text(f"Запись на «{tasting.title}»\n\nВведите ваше имя:")
    await callback.answer()


@router.message(RegistrationStates.input_name)
async def input_name(message: types.Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Имя должно содержать хотя бы 2 символа. Попробуйте ещё раз:")
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(RegistrationStates.input_phone)
    await message.answer("Введите ваш номер телефона (например, +7 (999) 123-45-67):")


@router.message(RegistrationStates.input_phone)
async def input_phone(message: types.Message, state: FSMContext) -> None:
    if not message.text or not validate_phone(message.text):
        await message.answer("Некорректный номер телефона. Введите в формате +7 (999) 123-45-67:")
        return
    await state.update_data(phone=message.text.strip())
    await state.set_state(RegistrationStates.input_guests)
    await message.answer("Сколько гостей будет с вами (включая вас)?", reply_markup=get_cancel_keyboard())


@router.message(RegistrationStates.input_guests)
async def input_guests(message: types.Message, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit() or int(message.text) < 1:
        await message.answer("Пожалуйста, введите корректное число гостей (минимум 1):")
        return
    await state.update_data(guests_count=int(message.text))
    await state.set_state(RegistrationStates.input_comment)
    await message.answer(
        "Есть ли у вас пожелания по винам или другие комментарии? (можно пропустить, отправив «-»):"
    )


@router.message(RegistrationStates.input_comment)
async def input_comment(message: types.Message, state: FSMContext) -> None:
    comment = message.text.strip() if message.text and message.text.strip() not in ("-", "—", ".") else None
    await state.update_data(comment=comment)
    data = await state.get_data()

    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tasting = await repo.get_by_id(data["tasting_id"])

    text = (
        f"📝 *Проверьте данные:*\n\n"
        f"*Мероприятие:* {tasting.title if tasting else '—'}\n"
        f"*Имя:* {data['name']}\n"
        f"*Телефон:* {data['phone']}\n"
        f"*Гостей:* {data['guests_count']}\n"
        f"*Комментарий:* {data['comment'] or '—'}\n\n"
        "Всё верно?"
    )
    await state.set_state(RegistrationStates.confirm)
    await message.answer(text, parse_mode="Markdown", reply_markup=get_confirm_keyboard())


@router.callback_query(F.data == "register_confirm")
async def confirm_registration(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    bot = callback.bot

    async with async_session_factory() as session:
        service = RegistrationService(session, bot)
        application, error = await service.register(
            tasting_id=data["tasting_id"],
            telegram_id=callback.from_user.id,
            name=data["name"],
            phone=data["phone"],
            guests_count=data.get("guests_count", 1),
            comment=data.get("comment"),
        )

    if error:
        await callback.message.edit_text(f"❌ {error}")
        await state.clear()
        await callback.message.answer("Главное меню:", reply_markup=get_main_menu())
        await callback.answer()
        return

    await callback.message.edit_text(REGISTRATION_CONFIRMATION, parse_mode="Markdown")

    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tasting = await repo.get_by_id(data["tasting_id"])

    if tasting:
        reminder = ReminderService(bot)
        await reminder.send_tasting_info(callback.from_user.id, tasting)

        scheduler = get_scheduler()
        scheduler.schedule_reminders(
            telegram_id=callback.from_user.id,
            tasting_title=tasting.title,
            date_str=tasting.date,
            time_str=tasting.time,
        )

    await state.clear()
    await callback.message.answer("Главное меню:", reply_markup=get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "register_cancel")
async def cancel_registration(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Запись отменена.")
    await callback.message.answer("Главное меню:", reply_markup=get_main_menu())
    await callback.answer()
