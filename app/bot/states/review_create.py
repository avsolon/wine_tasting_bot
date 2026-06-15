from aiogram.fsm.state import State, StatesGroup


class ReviewCreateStates(StatesGroup):
    input_author = State()
    input_text = State()
    input_rating = State()
    input_source_url = State()
    confirm = State()


class ReviewEditStates(StatesGroup):
    select_field = State()
    input_value = State()
