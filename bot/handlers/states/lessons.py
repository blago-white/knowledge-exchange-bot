from aiogram.fsm.state import StatesGroup, State


class LessonCreationForm(StatesGroup):
    add_datetime = State()
    add_duration = State()
