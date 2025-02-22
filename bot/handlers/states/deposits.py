from aiogram.fsm.state import State


class DepositFormState(State):
    set_amount = State()
    approvation = State()
