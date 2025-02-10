from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline import get_sell_approve_kb
from ..states.sales import SellStudentForm
from ..common.validators.telegram import get_validated_tid
from services.worker import WorkersService
from services.user import UserService
from ..providers import provide_model_service

router = Router(name=__name__)


@router.message(Command("sell"))
@provide_model_service(WorkersService)
async def sell_student_info(
        message: Message,
        state: FSMContext,
        workers_service: WorkersService):
    return await message.reply(
        text="<i>ℹ Продать ученика вы можете зная telegram id репетитора, "
             "которому продаете</i>\n\n"
             "Для продажи: Меню > Мои ученики > *Ученик для продажи* > "
             "Нажмите 'Продать' и после введите id получателя\n\n"
             "Когда получатель примет предложение, по мере проведения уроков"
             "вам будет начисляться оплата на счет"
    )


@router.message(SellStudentForm.enter_recipient_id)
@provide_model_service(WorkersService)
async def enter_recipient_id(
        message: Message,
        state: FSMContext,
        workers_service: WorkersService):
    try:
        recipient_id = get_validated_tid(telegram_id_input=message.text)
    except ValueError as validation_error:
        return await message.reply(
            text=f"❌{str(validation_error)}\n\n<i>Попробуйте еще разок!</i>"
        )
    except:
        return await message.reply(
            text=f"❌Что-то пошло не так...\n\n<i>Попробуйте еще разок!</i>"
        )

    if not await type(workers_service)(worker_id=recipient_id).is_worker:
        return await message.reply(text="🤷 <b>Такого репетитора не находим, "
                                        "если что - пишите в поддержку, поможем</b>")

    data = await state.get_data()

    await state.set_data(data=data | dict(recipient_id=recipient_id))

    await state.set_state(state=SellStudentForm.enter_cost)

    await message.reply("✅ <b>Узнали</b>, а за сколько ₽ вы хотите его продать?")


@router.message(SellStudentForm.enter_cost)
@provide_model_service(WorkersService)
async def enter_cost(
        message: Message,
        state: FSMContext,
        workers_service: WorkersService):
    try:
        cost = int(message.text.rstrip().lstrip())

        assert cost > 0, ValueError
    except:
        return await message.reply("❌ Не распознаем <b>целое</b> число :(")

    data = await state.get_data()

    await state.set_data(data | dict(cost=cost))

    await state.set_state()

    await message.reply(
        text="✔ Так, форму заполнили, вы подтверждаете продажу?",
        reply_markup=get_sell_approve_kb()
    )
