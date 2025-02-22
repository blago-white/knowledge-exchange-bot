from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from services.deposits import DepositsService
from services.user import UserService, UserType
from models.deposits import Deposit
from keyboards.deposits import get_payment_approve_kb

from .utils.data import MakeDepositData, DepositMakingApprovationData, \
    DepositPaymentApproveData
from ..states.deposits import DepositFormState
from ..providers import provide_model_service

router = Router(name=__name__)


@router.callback_query(MakeDepositData.filter())
async def make_deposit(
        query: CallbackQuery,
        callback_data: MakeDepositData,
        state: FSMContext):
    await query.answer()

    await state.set_state(state=DepositFormState.set_amount)

    await query.message.bot.send_message(
        chat_id=query.message.chat.id,
        text="<b>₽</b> Введите сумму пополнения в рублях:"
    )


@router.callback_query(DepositMakingApprovationData.filter())
@provide_model_service(DepositsService)
async def commit_approvation(
        query: CallbackQuery,
        callback_data: DepositMakingApprovationData,
        state: FSMContext,
        deposits_service: DepositsService):
    if callback_data.approve:
        data = await state.get_data()

        try:
            deposit = await deposits_service.repository.create(
                deposit=Deposit(
                    amount=data.get("amount"),
                    user_telegram_id=query.message.chat.id
                )
            )
        except Exception as e:
            print(e)
            return await query.message.edit_text(
                "❌ Возникла непредвиденная ошибка, "
                "напишите в поддержку :( \n\n/start"
            )
        await query.message.edit_text(
            text="✅ <b>Создали платеж, действуйте по плану ниже:</b>\n\n"
                 "➖ Переведите точно эту сумму через <i>СБП</i>: \n"
                 "<code>8 995 248 17 51</code> | <i>🟢 Сбер</i>\n"
                 f"⚠ ОБЯЗАТЕЛЬНО ДОБАВЬТЕ ЭТО ОПИСАНИЕ К ПЛАТЕЖУ: <code>Оплата #{deposit.id}</code>\n"
                 f"⚠ Если нет возможности добавить платеж, напишите инициалы отправителя и дату перевода в техподдержку: /support\n\n"
                 "➖ После перевода, нажмите кнопку ниже ⤵\n\n"
                 "➖ Ожидайте подтверждения платежа от администратора, это займет не более нескольки часов, зачастую - 5-15 мин.\n",
            reply_markup=get_payment_approve_kb()
        )
    else:
        await query.message.edit_text(
            text="❌ Отменили пополнение \n\n/start"
        )


@router.callback_query(DepositPaymentApproveData.filter(F.admin_view == False))
@provide_model_service(DepositsService)
async def set_paid(
        query: CallbackQuery,
        callback_data: DepositMakingApprovationData,
        state: FSMContext,
        deposits_service: DepositsService):
    try:
        deposit = await deposits_service.repository.set_paid(
            telegram_id=query.message.chat.id
        )
    except Exception as e:
        print(e, str(e))
        return await query.message.edit_text(
            text="❌ Напишите в поддержку - /support, не удалось установить статус"
        )

    await query.bot.send_message(
        chat_id=935570478,
        text=f"❗️❗️❗️ Поступил платеж - <code>ID: {deposit.id}</code>",
        reply_markup=get_payment_approve_kb(admin_view=True, deposit_id=deposit.id)
    )


@router.callback_query(DepositPaymentApproveData.filter(F.admin_view == True))
@provide_model_service(DepositsService, UserService)
async def set_success(
        query: CallbackQuery,
        callback_data: DepositPaymentApproveData,
        state: FSMContext,
        deposits_service: DepositsService,
        user_service: UserService):
    if query.message.chat.id == 935570478:
        await query.answer()

        deposit = await deposits_service.repository.get(
            pk=callback_data.to_admin_deposit_id
        )

        _, deposit_recipient = await user_service.get_user(
            telegram_id=deposit.user_telegram_id
        )

        try:
            await deposits_service.set_success(
                deposit=deposit,
                user=deposit_recipient
            )
        except Exception as e:
            print(e)
            return await query.message.edit_text("❌ Не удалось")

        await query.bot.send_message(
            chat_id=deposit.user_telegram_id,
            text=f"✅ Ваш депозит <b>{deposit.amount}₽</b> подтвержден, деньги поступили на баланс!"
        )

        await query.message.edit_text("✅ Депозит подтвержден")
