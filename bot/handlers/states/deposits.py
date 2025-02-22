from aiogram.fsm.state import StatesGroup, State


class DepositFormState(StatesGroup):
    set_amount = State()
    approvation = State()
