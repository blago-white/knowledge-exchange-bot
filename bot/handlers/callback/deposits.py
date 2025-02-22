from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .utils.data import MakeDepositData, DepositMakingApprovationData
from ..states.deposits import DepositFormState

router = Router(name=__name__)


@router.callback_query(MakeDepositData.filter())
async def make_deposit(query: CallbackQuery,
                       callback_data: MakeDepositData,
                       state: FSMContext):
    await query.answer()

    await state.set_state(state=DepositFormState.set_amount)

    await query.message.bot.send_message(
        chat_id=query.message.chat.id,
        text="<b>₽</b> Введите сумму пополнения в рублях:"
    )


@router.callback_query(DepositMakingApprovationData.filter())
async def commit_approvation(query: CallbackQuery,
                             callback_data: DepositMakingApprovationData,
                             state: FSMContext):
    if callback_data.approve:
        ...
    else:
        await query.message.edit_text(
            text="❌ Отменили пополнение \n\n/start"
        )
