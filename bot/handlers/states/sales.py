from aiogram.fsm.state import State, StatesGroup


class SellStudentForm(StatesGroup):
    enter_recipient_id = State()
    enter_cost = State()
