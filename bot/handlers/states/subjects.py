from aiogram.fsm.state import StatesGroup, State


class EditSubjectForm(StatesGroup):
    edit_field = State()
