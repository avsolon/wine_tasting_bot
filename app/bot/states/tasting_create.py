from aiogram.fsm.state import State, StatesGroup


class TastingCreateStates(StatesGroup):
    input_title = State()
    input_date = State()
    input_time = State()
    input_price = State()
    input_seats = State()
    input_description = State()
    confirm = State()


class TastingEditStates(StatesGroup):
    select_field = State()
    input_value = State()
