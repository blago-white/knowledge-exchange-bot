from aiogram import F
from aiogram.filters import and_f
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import (ReplyKeyboardRemove,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup)

from keyboards.inline import (get_selled_list_inline_kb,
                              get_accept_sell_offer_kb)
from models.worker import Worker
from models.lesson import Subject
from services.worker import WorkersService
from services.lesson import SubjectsService

from ..callback.utils import data
from ..common.utils.messages import generate_lesson_data_message_text
from ..providers import provide_model_service
from ..replies import LESSON_DATA_MESSAGE
from handlers.states import sales as sales_states

router = Router(name=__name__)


@router.callback_query(data.MakeWithdrawData.filter())
async def make_withdraw(
        query: CallbackQuery,
        callback_data: data.ShowLessonInfoData,
        state: FSMContext):
    await query.answer("Уже делаем этот раздел!")


@router.callback_query(data.SelledStudentsList.filter())
@provide_model_service(WorkersService)
async def view_sold(
        query: CallbackQuery,
        callback_data: data.ShowLessonInfoData,
        state: FSMContext,
        workers_service: WorkersService):
    selled = await workers_service.get_selled_students()

    await query.message.edit_text(
        text="⚜ <b>Ваши продажи:</b>" if len(
            selled) else "⚜ <b>Продаж еще не было :(</b>",
        reply_markup=get_selled_list_inline_kb(selled=selled)
    )


@router.callback_query(data.SellStudentData.filter())
async def sell_student(
        query: CallbackQuery,
        callback_data: data.SellStudentData,
        state: FSMContext):
    await state.set_state(sales_states.SellStudentForm.enter_recipient_id)

    await state.set_data(data=dict(subject_id=callback_data.subject_id))

    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text="👤 Отправьте <i>telegram id</i> получателя ученика"
    )


@router.callback_query(data.SellApprovationData.filter())
@provide_model_service(WorkersService, SubjectsService)
async def commit_sell_offer_sending(
        query: CallbackQuery,
        callback_data: data.SellApprovationData,
        state: FSMContext,
        workers_service: WorkersService,
        subjects_service: SubjectsService):
    if callback_data.approve:
        data_: dict = await state.get_data()

        subjects_service.subject_id = data_.get("subject_id")

        try:
            offer = await workers_service.sell_student(
                buyer_worker_id=data_.get("recipient_id"),
                subject_id=subjects_service.subject_id,
                cost=data_.get("cost")
            )
        except Exception as e:
            print(e)
            await query.message.edit_text(
                text="❌ Что-то пошло не так("
            )
        else:
            subject: Subject = await subjects_service.repository.get(
                pk=subjects_service.subject_id
            )

            await query.bot.send_message(
                chat_id=data_.get("recipient_id"),
                text="🔥🔥🔥 <b>Вам пришло предложение на покупку ученика!</b>\n"
                     f"Ученик — {subject.student.name} [{subject.student.city}]\n"
                     f"Предмет — {subject.title}\n"
                     f"<i>{subject.description or "Описание не задано"}</i>\n\n"
                     f"О ученике — {subject.student.description}\n\n"
                     f"<b>Сумма продажи — {offer.cost}, оплата за час: {subject.rate}</b>",
                reply_markup=get_accept_sell_offer_kb(
                    offer_id=offer.subject_id
                )
            )

            await query.message.edit_text(
                text="✔ <b>Отправили предложение о покупке получателю</b>, "
                     "теперь ждем когда его подтвердят, "
                     "а статус лида смотрите в "
                     "проданных учениках в меню!"
            )
    else:
        await query.message.edit_text(
            text="❌ Отменено"
        )

    await state.clear()


@router.callback_query(data.SellOfferAcceptingData.filter(
    F.offer_id != None
))
@provide_model_service(WorkersService)
async def set_accept_value_sell_offer(
        query: CallbackQuery,
        callback_data: data.SellOfferAcceptingData,
        state: FSMContext,
        workers_service: WorkersService):
    await query.message.edit_reply_markup()

    try:
        offer = await workers_service.accept_sell_offer(
            subject_id=callback_data.offer_id,
            accept=callback_data.accept
        )
    except Exception as e:
        print(e)

        return await query.message.edit_text(
            text="❌ <b>Что то пошло не так, напишите в "
                 "поддержку если вы хотели принять оффер</b>",
        )
    if callback_data.accept:
        await query.message.edit_text(
            text="✅ <b>Вы получили ученика, он появился в разделе *Мои ученики*</b>\n"
                 "Проводите уроки, "
                 "и оплачивайте ученика, после полной оплаты вы сможете:\n"
                 "- Продать ученика\n"
                 "- Получить контакты ученика\n"
        )
        await query.bot.send_message(
            chat_id=offer.seller_id,
            text="⚡⚡⚡ <b>Ваш запрос на продажу приняли</b>\n"
                 f"Ученик по предмету {offer.subject.title} и стоимостью {offer.cost}\n"
                 f"Был куплен статус оплат смотрите в главном меню > проданные ученики!"
        )
