from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    select_tasting = State()
    input_name = State()
    input_phone = State()
    input_guests = State()
    input_comment = State()
    confirm = State()
