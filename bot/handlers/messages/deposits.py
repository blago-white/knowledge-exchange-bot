from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.deposits import get_deposit_approvation_kb

from ..states.deposits import DepositFormState


router = Router(name=__name__)


@router.message(DepositFormState.set_amount)
async def enter_deposit_amount(message: Message,
                               state: FSMContext):
    try:
        amount = int(message)

        if amount < 100 or amount > 30000:
            raise ValueError("<b>Неверная сумма</b>, она должна быть не менее 100₽ и не более 30к₽")
    except ValueError as value_error:
        return await message.reply(
            text=f"❌ {str(value_error)}"
        )
    except:
        return await message.reply(
            text="❌ <b>Кажется, вы ввели не число</b> (либо не целое число, а такое принять не можем)"
        )

    data = state.get_data()

    data |= {"amount": amount}

    await state.set_data(data=data)

    await message.reply(
        text="🟢 Отлично, пополняем?!",
        reply_markup=get_deposit_approvation_kb()
    )
