from aiogram.fsm.state import State, StatesGroup


class WineCreateStates(StatesGroup):
    select_tasting = State()
    input_name = State()
    input_country = State()
    input_region = State()
    input_grape = State()
    input_description = State()
    input_photo = State()
    confirm = State()


class WineEditStates(StatesGroup):
    select_field = State()
    input_value = State()
