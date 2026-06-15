from aiogram import Router, types
from aiogram.filters import CommandStart
from app.core.constants import WELCOME_MESSAGE
from app.bot.keyboards.main_menu import get_main_menu
from app.database.session import async_session_factory
from app.repositories.user_repository import UserRepository

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    async with async_session_factory() as session:
        repo = UserRepository(session)
        user = await repo.get_by_telegram_id(message.from_user.id)
        if not user:
            await repo.create(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
            )

    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu(),
        parse_mode="Markdown",
    )
