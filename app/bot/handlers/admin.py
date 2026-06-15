from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.filters.admin import AdminFilter
from app.bot.keyboards.main_menu import get_main_menu
from app.bot.keyboards.admin_menu import (
    get_admin_menu,
    get_tasting_management_keyboard,
    get_wine_management_keyboard,
    get_gallery_management_keyboard,
    get_review_management_keyboard,
    get_application_list_keyboard,
    get_tasting_list_keyboard,
    get_wine_list_keyboard,
    get_tasting_selection_for_wine_keyboard,
    get_tasting_selection_for_gallery_keyboard,
    get_confirm_delete_keyboard,
    get_settings_keyboard,
    get_admin_cancel_keyboard,
)
from app.bot.states.tasting_create import TastingCreateStates, TastingEditStates
from app.bot.states.wine_create import WineCreateStates, WineEditStates
from app.bot.states.review_create import ReviewCreateStates, ReviewEditStates
from app.bot.states.gallery_create import GalleryCreateStates
from app.database.session import async_session_factory
from app.repositories.tasting_repository import TastingRepository
from app.repositories.wine_repository import WineRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.photo_repository import PhotoRepository
from app.repositories.application_repository import ApplicationRepository
from app.services.statistics.statistics_service import StatisticsService
from app.utils.text_formatter import format_application_card, format_statistics

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.message(Command("admin"))
async def admin_panel(message: types.Message) -> None:
    await message.answer(
        "🔐 *Административная панель*\n\nВыберите раздел:",
        parse_mode="Markdown",
        reply_markup=get_admin_menu(),
    )


@router.message(F.text == "🔙 Назад")
async def admin_back_to_main(message: types.Message) -> None:
    await message.answer("Главное меню:", reply_markup=get_main_menu())


# ── Дегустации ──────────────────────────────────────────────────────────────

@router.message(F.text == "📅 Дегустации")
async def manage_tastings(message: types.Message) -> None:
    await message.answer(
        "Управление дегустациями:",
        reply_markup=get_tasting_management_keyboard(),
    )


@router.callback_query(F.data == "admin_tasting_create")
async def create_tasting_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TastingCreateStates.input_title)
    await callback.message.edit_text("Введите название дегустации:", reply_markup=get_admin_cancel_keyboard())
    await callback.answer()


@router.message(TastingCreateStates.input_title)
async def create_tasting_title(message: types.Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Название должно содержать хотя бы 2 символа:")
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(TastingCreateStates.input_date)
    await message.answer("Введите дату (в формате ГГГГ-ММ-ДД):")


@router.message(TastingCreateStates.input_date)
async def create_tasting_date(message: types.Message, state: FSMContext) -> None:
    from app.utils.datetime_helper import parse_date
    if not message.text or not parse_date(message.text):
        await message.answer("Некорректная дата. Введите в формате ГГГГ-ММ-ДД:")
        return
    await state.update_data(date=message.text.strip())
    await state.set_state(TastingCreateStates.input_time)
    await message.answer("Введите время (например, 19:00):")


@router.message(TastingCreateStates.input_time)
async def create_tasting_time(message: types.Message, state: FSMContext) -> None:
    await state.update_data(time=message.text.strip())
    await state.set_state(TastingCreateStates.input_price)
    await message.answer("Введите стоимость (в рублях, только число):")


@router.message(TastingCreateStates.input_price)
async def create_tasting_price(message: types.Message, state: FSMContext) -> None:
    try:
        price = float(message.text.strip())
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректную стоимость (число):")
        return
    await state.update_data(price=price)
    await state.set_state(TastingCreateStates.input_seats)
    await message.answer("Введите количество мест:")


@router.message(TastingCreateStates.input_seats)
async def create_tasting_seats(message: types.Message, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit() or int(message.text) < 1:
        await message.answer("Введите корректное число мест:")
        return
    await state.update_data(total_seats=int(message.text))
    await state.set_state(TastingCreateStates.input_description)
    await message.answer("Введите описание дегустации:")


@router.message(TastingCreateStates.input_description)
async def create_tasting_description(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.strip())
    data = await state.get_data()

    text = (
        "📅 *Проверьте данные:*\n\n"
        f"*Название:* {data['title']}\n"
        f"*Дата:* {data['date']}\n"
        f"*Время:* {data['time']}\n"
        f"*Стоимость:* {data['price']} ₽\n"
        f"*Мест:* {data['total_seats']}\n"
        f"*Описание:* {data['description']}\n\n"
        "Всё верно?"
    )
    await state.set_state(TastingCreateStates.confirm)
    await message.answer(text, parse_mode="Markdown", reply_markup=get_confirm_delete_keyboard("tasting_create", 0))


@router.callback_query(F.data == "admin_confirm_delete:tasting_create:0")
async def create_tasting_confirm(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        await repo.create(
            title=data["title"],
            date=data["date"],
            time=data["time"],
            price=data["price"],
            total_seats=data["total_seats"],
            description=data["description"],
        )
    await state.clear()
    await callback.message.edit_text("✅ Дегустация успешно создана!")
    await callback.message.answer("Админ-панель:", reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_tasting_edit_list")
async def edit_tasting_list(callback: types.CallbackQuery) -> None:
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tastings = await repo.get_all()
    await callback.message.edit_text(
        "Выберите дегустацию для редактирования:",
        reply_markup=get_tasting_list_keyboard(tastings, "edit"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_tasting_edit:"))
async def edit_tasting_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    tasting_id = int(callback.data.split(":")[1])
    await state.update_data(tasting_id=tasting_id)
    await state.set_state(TastingEditStates.select_field)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Название", callback_data="field:title")],
        [InlineKeyboardButton(text="Дата", callback_data="field:date")],
        [InlineKeyboardButton(text="Время", callback_data="field:time")],
        [InlineKeyboardButton(text="Стоимость", callback_data="field:price")],
        [InlineKeyboardButton(text="Описание", callback_data="field:description")],
        [InlineKeyboardButton(text="Количество мест", callback_data="field:total_seats")],
        [InlineKeyboardButton(text="Статус", callback_data="field:status")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")],
    ])
    await callback.message.edit_text("Что хотите изменить?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("field:"), TastingEditStates.select_field)
async def edit_tasting_field(callback: types.CallbackQuery, state: FSMContext) -> None:
    field = callback.data.split(":")[1]
    await state.update_data(field=field)
    await state.set_state(TastingEditStates.input_value)
    await callback.message.edit_text(f"Введите новое значение для поля «{field}»:")
    await callback.answer()


@router.message(TastingEditStates.input_value)
async def edit_tasting_value(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data["field"]
    value = message.text.strip()

    if field in ("total_seats", "price"):
        try:
            value = int(value) if field == "total_seats" else float(value)
        except ValueError:
            await message.answer("Введите корректное число:")
            return

    async with async_session_factory() as session:
        repo = TastingRepository(session)
        await repo.update(data["tasting_id"], **{field: value})

    await state.clear()
    await message.answer(f"✅ Поле «{field}» обновлено!")
    await message.answer("Админ-панель:", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_tasting_delete_list")
async def delete_tasting_list(callback: types.CallbackQuery) -> None:
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tastings = await repo.get_all()
    await callback.message.edit_text(
        "Выберите дегустацию для удаления:",
        reply_markup=get_tasting_list_keyboard(tastings, "delete"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_tasting_delete:"))
async def delete_tasting_confirm(callback: types.CallbackQuery) -> None:
    tasting_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить эту дегустацию?",
        reply_markup=get_confirm_delete_keyboard("tasting", tasting_id),
    )
    await callback.answer()


# ── Вина ─────────────────────────────────────────────────────────────────────

@router.message(F.text == "🍷 Вина")
async def manage_wines(message: types.Message) -> None:
    await message.answer("Управление винами:", reply_markup=get_wine_management_keyboard())


@router.callback_query(F.data == "admin_wine_create")
async def create_wine_select_tasting(callback: types.CallbackQuery, state: FSMContext) -> None:
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tastings = await repo.get_all()
    await state.set_state(WineCreateStates.select_tasting)
    await callback.message.edit_text(
        "Выберите дегустацию для добавления вина:",
        reply_markup=get_tasting_selection_for_wine_keyboard(tastings),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_wine_select_tasting:"))
async def create_wine_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    tasting_id = int(callback.data.split(":")[1])
    await state.update_data(tasting_id=tasting_id)
    await state.set_state(WineCreateStates.input_name)
    await callback.message.edit_text("Введите название вина:")
    await callback.answer()


@router.message(WineCreateStates.input_name)
async def create_wine_country(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(WineCreateStates.input_country)
    await message.answer("Введите страну производства (можно пропустить, отправив «-»):")


@router.message(WineCreateStates.input_country)
async def create_wine_region(message: types.Message, state: FSMContext) -> None:
    val = message.text.strip() if message.text and message.text.strip() != "-" else None
    await state.update_data(country=val)
    await state.set_state(WineCreateStates.input_region)
    await message.answer("Введите регион (можно пропустить, отправив «-»):")


@router.message(WineCreateStates.input_region)
async def create_wine_grape(message: types.Message, state: FSMContext) -> None:
    val = message.text.strip() if message.text and message.text.strip() != "-" else None
    await state.update_data(region=val)
    await state.set_state(WineCreateStates.input_grape)
    await message.answer("Введите сорт винограда (можно пропустить, отправив «-»):")


@router.message(WineCreateStates.input_grape)
async def create_wine_description(message: types.Message, state: FSMContext) -> None:
    val = message.text.strip() if message.text and message.text.strip() != "-" else None
    await state.update_data(grape=val)
    await state.set_state(WineCreateStates.input_description)
    await message.answer("Введите описание вина:")


@router.message(WineCreateStates.input_description)
async def create_wine_photo(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text.strip())
    await state.set_state(WineCreateStates.input_photo)
    await message.answer("Отправьте фото вина (или отправьте «-» чтобы пропустить):")


@router.message(WineCreateStates.input_photo)
async def create_wine_confirm(message: types.Message, state: FSMContext) -> None:
    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    elif message.text and message.text.strip() == "-":
        photo_file_id = None
    else:
        await message.answer("Отправьте фото или «-» для пропуска:")
        return

    await state.update_data(photo_file_id=photo_file_id)
    data = await state.get_data()

    text = (
        "🍷 *Проверьте данные:*\n\n"
        f"*Название:* {data['name']}\n"
        f"*Страна:* {data.get('country', '—') or '—'}\n"
        f"*Регион:* {data.get('region', '—') or '—'}\n"
        f"*Сорт:* {data.get('grape', '—') or '—'}\n"
        f"*Описание:* {data['description']}\n"
        f"*Фото:* {'есть' if data['photo_file_id'] else 'нет'}\n\n"
        "Всё верно?"
    )
    await state.set_state(WineCreateStates.confirm)
    await message.answer(text, parse_mode="Markdown", reply_markup=get_confirm_delete_keyboard("wine_create", 0))


@router.callback_query(F.data == "admin_confirm_delete:wine_create:0")
async def create_wine_execute(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    async with async_session_factory() as session:
        repo = WineRepository(session)
        await repo.create(
            tasting_id=data["tasting_id"],
            name=data["name"],
            country=data.get("country"),
            region=data.get("region"),
            grape=data.get("grape"),
            description=data["description"],
            photo_file_id=data.get("photo_file_id"),
        )
    await state.clear()
    await callback.message.edit_text("✅ Вино успешно добавлено!")
    await callback.message.answer("Админ-панель:", reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_wine_edit_list")
async def edit_wine_list(callback: types.CallbackQuery) -> None:
    async with async_session_factory() as session:
        repo = WineRepository(session)
        wines = await repo.get_all()
    await callback.message.edit_text(
        "Выберите вино для редактирования:",
        reply_markup=get_wine_list_keyboard(wines, "edit"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_wine_edit:"))
async def edit_wine_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    wine_id = int(callback.data.split(":")[1])
    await state.update_data(wine_id=wine_id)
    await state.set_state(WineEditStates.select_field)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Название", callback_data="wfield:name")],
        [InlineKeyboardButton(text="Страна", callback_data="wfield:country")],
        [InlineKeyboardButton(text="Регион", callback_data="wfield:region")],
        [InlineKeyboardButton(text="Сорт", callback_data="wfield:grape")],
        [InlineKeyboardButton(text="Описание", callback_data="wfield:description")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")],
    ])
    await callback.message.edit_text("Что хотите изменить?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("wfield:"), WineEditStates.select_field)
async def edit_wine_field(callback: types.CallbackQuery, state: FSMContext) -> None:
    field = callback.data.split(":")[1]
    await state.update_data(field=field)
    await state.set_state(WineEditStates.input_value)
    await callback.message.edit_text(f"Введите новое значение для поля «{field}»:")
    await callback.answer()


@router.message(WineEditStates.input_value)
async def edit_wine_value(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data["field"]
    async with async_session_factory() as session:
        repo = WineRepository(session)
        await repo.update(data["wine_id"], **{field: message.text.strip()})
    await state.clear()
    await message.answer(f"✅ Поле «{field}» обновлено!")
    await message.answer("Админ-панель:", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_wine_delete_list")
async def delete_wine_list(callback: types.CallbackQuery) -> None:
    async with async_session_factory() as session:
        repo = WineRepository(session)
        wines = await repo.get_all()
    await callback.message.edit_text(
        "Выберите вино для удаления:",
        reply_markup=get_wine_list_keyboard(wines, "delete"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_wine_delete:"))
async def delete_wine_confirm(callback: types.CallbackQuery) -> None:
    wine_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить это вино?",
        reply_markup=get_confirm_delete_keyboard("wine", wine_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm_delete:wine:"))
async def delete_wine_execute(callback: types.CallbackQuery) -> None:
    wine_id = int(callback.data.split(":")[2])
    async with async_session_factory() as session:
        repo = WineRepository(session)
        await repo.delete(wine_id)
    await callback.message.edit_text("✅ Вино удалено.")
    await callback.message.answer("Админ-панель:", reply_markup=get_admin_menu())
    await callback.answer()


# ── Галерея ──────────────────────────────────────────────────────────────────

@router.message(F.text == "📸 Галерея")
async def manage_gallery(message: types.Message) -> None:
    await message.answer("Управление галереей:", reply_markup=get_gallery_management_keyboard())


@router.callback_query(F.data == "admin_gallery_add")
async def add_gallery_select_tasting(callback: types.CallbackQuery, state: FSMContext) -> None:
    async with async_session_factory() as session:
        repo = TastingRepository(session)
        tastings = await repo.get_all()
    await state.set_state(GalleryCreateStates.select_tasting)
    await callback.message.edit_text(
        "Привяжите фото к дегустации (или выберите «Без привязки»):",
        reply_markup=get_tasting_selection_for_gallery_keyboard(tastings),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_gallery_tasting:"))
async def add_gallery_photo(callback: types.CallbackQuery, state: FSMContext) -> None:
    tasting_id = int(callback.data.split(":")[1])
    await state.update_data(tasting_id=tasting_id if tasting_id else None)
    await state.set_state(GalleryCreateStates.input_photo)
    await callback.message.edit_text("Отправьте фото для добавления в галерею:")
    await callback.answer()


@router.message(GalleryCreateStates.input_photo)
async def add_gallery_description(message: types.Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото:")
        return
    await state.update_data(file_id=message.photo[-1].file_id)
    await state.set_state(GalleryCreateStates.input_description)
    await message.answer("Введите описание фото (или отправьте «-» чтобы пропустить):")


@router.message(GalleryCreateStates.input_description)
async def add_gallery_confirm(message: types.Message, state: FSMContext) -> None:
    description = message.text.strip() if message.text and message.text.strip() != "-" else None
    await state.update_data(description=description)
    data = await state.get_data()

    async with async_session_factory() as session:
        repo = PhotoRepository(session)
        await repo.create(
            file_id=data["file_id"],
            tasting_id=data.get("tasting_id"),
            description=data.get("description"),
        )

    await state.clear()
    await message.answer("✅ Фото добавлено в галерею!")
    await message.answer("Админ-панель:", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_gallery_delete_list")
async def delete_gallery_list(callback: types.CallbackQuery) -> None:
    async with async_session_factory() as session:
        repo = PhotoRepository(session)
        photos = await repo.get_all()

    if not photos:
        await callback.message.edit_text("Галерея пуста.")
        await callback.answer()
        return

    keyboard_buttons = []
    for p in photos[:20]:
        desc = p.description or f"Фото #{p.id}"
        keyboard_buttons.append([
            InlineKeyboardButton(text=desc, callback_data=f"admin_gallery_delete:{p.id}")
        ])
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text("Выберите фото для удаления:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_gallery_delete:"))
async def delete_gallery_execute(callback: types.CallbackQuery) -> None:
    photo_id = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        repo = PhotoRepository(session)
        await repo.delete(photo_id)
    await callback.message.edit_text("✅ Фото удалено.")
    await callback.message.answer("Админ-панель:", reply_markup=get_admin_menu())
    await callback.answer()


# ── Отзывы ───────────────────────────────────────────────────────────────────

@router.message(F.text == "⭐ Отзывы")
async def manage_reviews(message: types.Message) -> None:
    await message.answer("Управление отзывами:", reply_markup=get_review_management_keyboard())


@router.callback_query(F.data == "admin_review_create")
async def create_review_author(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReviewCreateStates.input_author)
    await callback.message.edit_text("Введите имя автора отзыва:")
    await callback.answer()


@router.message(ReviewCreateStates.input_author)
async def create_review_text(message: types.Message, state: FSMContext) -> None:
    await state.update_data(author_name=message.text.strip())
    await state.set_state(ReviewCreateStates.input_text)
    await message.answer("Введите текст отзыва:")


@router.message(ReviewCreateStates.input_text)
async def create_review_rating(message: types.Message, state: FSMContext) -> None:
    await state.update_data(text=message.text.strip())
    await state.set_state(ReviewCreateStates.input_rating)
    await message.answer("Введите рейтинг (от 1 до 5) или отправьте «-» чтобы пропустить:")


@router.message(ReviewCreateStates.input_rating)
async def create_review_url(message: types.Message, state: FSMContext) -> None:
    rating = None
    if message.text and message.text.strip().isdigit():
        val = int(message.text.strip())
        if 1 <= val <= 5:
            rating = val
    await state.update_data(rating=rating)
    await state.set_state(ReviewCreateStates.input_source_url)
    await message.answer("Введите ссылку на источник (или отправьте «-» чтобы пропустить):")


@router.message(ReviewCreateStates.input_source_url)
async def create_review_confirm(message: types.Message, state: FSMContext) -> None:
    source_url = message.text.strip() if message.text and message.text.strip() != "-" else None
    await state.update_data(source_url=source_url)
    data = await state.get_data()

    async with async_session_factory() as session:
        repo = ReviewRepository(session)
        await repo.create(
            author_name=data["author_name"],
            text=data["text"],
            rating=data.get("rating"),
            source_url=data.get("source_url"),
        )
    await state.clear()
    await message.answer("✅ Отзыв успешно добавлен!")
    await message.answer("Админ-панель:", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_review_edit_list")
async def edit_review_list(callback: types.CallbackQuery) -> None:
    async with async_session_factory() as session:
        repo = ReviewRepository(session)
        reviews = await repo.get_all()

    if not reviews:
        await callback.message.edit_text("Нет отзывов.")
        await callback.answer()
        return

    keyboard_buttons = []
    for r in reviews:
        text = r.author_name[:30]
        keyboard_buttons.append([
            InlineKeyboardButton(text=text, callback_data=f"admin_review_edit:{r.id}")
        ])
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text("Выберите отзыв для редактирования:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_review_edit:"))
async def edit_review_field(callback: types.CallbackQuery, state: FSMContext) -> None:
    review_id = int(callback.data.split(":")[1])
    await state.update_data(review_id=review_id)
    await state.set_state(ReviewEditStates.select_field)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Имя автора", callback_data="rfield:author_name")],
        [InlineKeyboardButton(text="Текст", callback_data="rfield:text")],
        [InlineKeyboardButton(text="Рейтинг", callback_data="rfield:rating")],
        [InlineKeyboardButton(text="Ссылка", callback_data="rfield:source_url")],
        [InlineKeyboardButton(text="Активен", callback_data="rfield:is_active")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")],
    ])
    await callback.message.edit_text("Что хотите изменить?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("rfield:"), ReviewEditStates.select_field)
async def edit_review_field_value(callback: types.CallbackQuery, state: FSMContext) -> None:
    field = callback.data.split(":")[1]
    await state.update_data(field=field)
    await state.set_state(ReviewEditStates.input_value)
    await callback.message.edit_text(f"Введите новое значение для поля «{field}»:")
    await callback.answer()


@router.message(ReviewEditStates.input_value)
async def edit_review_save(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data["field"]
    value = message.text.strip()
    if field == "is_active":
        value = value.lower() in ("да", "yes", "1", "true")
    elif field == "rating":
        try:
            value = int(value) if value.isdigit() else None
        except ValueError:
            value = None

    async with async_session_factory() as session:
        repo = ReviewRepository(session)
        await repo.update(data["review_id"], **{field: value})
    await state.clear()
    await message.answer(f"✅ Поле «{field}» обновлено!")
    await message.answer("Админ-панель:", reply_markup=get_admin_menu())


@router.callback_query(F.data == "admin_review_delete_list")
async def delete_review_list(callback: types.CallbackQuery) -> None:
    async with async_session_factory() as session:
        repo = ReviewRepository(session)
        reviews = await repo.get_all()

    if not reviews:
        await callback.message.edit_text("Нет отзывов.")
        await callback.answer()
        return

    keyboard_buttons = []
    for r in reviews:
        keyboard_buttons.append([
            InlineKeyboardButton(text=r.author_name, callback_data=f"admin_review_delete:{r.id}")
        ])
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text("Выберите отзыв для удаления:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_review_delete:"))
async def delete_review_confirm(callback: types.CallbackQuery) -> None:
    review_id = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        repo = ReviewRepository(session)
        await repo.delete(review_id)
    await callback.message.edit_text("✅ Отзыв удален.")
    await callback.message.answer("Админ-панель:", reply_markup=get_admin_menu())
    await callback.answer()


# ── Заявки ───────────────────────────────────────────────────────────────────

@router.message(F.text == "📋 Заявки")
async def manage_applications(message: types.Message) -> None:
    async with async_session_factory() as session:
        repo = ApplicationRepository(session)
        applications = await repo.get_all()

    if not applications:
        await message.answer("Нет заявок.")
        return

    await message.answer(
        "Список заявок:",
        reply_markup=get_application_list_keyboard(applications),
    )


@router.callback_query(F.data.startswith("admin_app_page:"))
async def applications_page(callback: types.CallbackQuery) -> None:
    page = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        repo = ApplicationRepository(session)
        applications = await repo.get_all()
    await callback.message.edit_text(
        "Список заявок:",
        reply_markup=get_application_list_keyboard(applications, page=page),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_app_view:"))
async def application_detail(callback: types.CallbackQuery) -> None:
    app_id = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        repo = ApplicationRepository(session)
        tasting_repo = TastingRepository(session)
        application = await repo.get_by_id(app_id)
        tasting = await tasting_repo.get_by_id(application.tasting_id) if application else None

    if not application:
        await callback.message.edit_text("Заявка не найдена.")
        await callback.answer()
        return

    text = format_application_card(application, tasting.title if tasting else "—")
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


# ── Статистика ───────────────────────────────────────────────────────────────

@router.message(F.text == "📊 Статистика")
async def show_statistics(message: types.Message) -> None:
    async with async_session_factory() as session:
        service = StatisticsService(session)
        stats = await service.get_statistics()

    text = format_statistics(
        total_tastings=stats["total_tastings"],
        total_applications=stats["total_applications"],
        total_guests=stats["total_guests"],
        avg_fill=stats["avg_fill"],
        next_event=stats["next_event"],
    )
    await message.answer(text, parse_mode="Markdown")


# ── Настройки ────────────────────────────────────────────────────────────────

@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: types.Message) -> None:
    await message.answer("Настройки:", reply_markup=get_settings_keyboard())


# ── Выход в пользовательское меню ──────────────────────────────────────────

@router.message(F.text == "🚪 Выход")
async def admin_exit(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Вы вышли из админ-панели. Главное меню:",
        reply_markup=get_main_menu(),
    )


# ── Общие коллбэки ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Админ-панель:")
    await callback.message.answer("Админ-панель:", reply_markup=get_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Действие отменено.")
    await callback.message.answer("Админ-панель:", reply_markup=get_admin_menu())
    await callback.answer()


# ── Ловушка для confirm_delete ───────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_confirm_delete:"))
async def generic_confirm_delete(callback: types.CallbackQuery) -> None:
    parts = callback.data.split(":")
    entity = parts[1]
    entity_id = int(parts[2])

    if entity == "tasting":
        async with async_session_factory() as session:
            repo = TastingRepository(session)
            await repo.delete(entity_id)
        await callback.message.edit_text("✅ Дегустация удалена.")
    elif entity == "wine":
        async with async_session_factory() as session:
            repo = WineRepository(session)
            await repo.delete(entity_id)
        await callback.message.edit_text("✅ Вино удалено.")
    else:
        await callback.message.edit_text("Неизвестный тип.")

    await callback.message.answer("Админ-панель:", reply_markup=get_admin_menu())
    await callback.answer()
