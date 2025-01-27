from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline import get_home_inline_kb, get_profile_inline_kb
from services.worker import WorkersService
from models.worker import Worker

from ..callback.utils.data import (RenderProfileData,
                                   UpdateProfileInfoData,
                                   ProfileUpdateField)
from ..common.utils.messages import generate_main_stats_message_text
from ..replies import ACCOUNT_DATA_MESSAGE, START_MESSAGE
from ..providers import provide_model_service
from ..states import profile as profile_states
from ..messages.common import start


router = Router(name=__name__)


@router.callback_query(RenderProfileData.filter(
    F.show_profile != None
))
@provide_model_service(WorkersService)
async def render_profile(
        query: CallbackQuery,
        callback_data: CallbackData,
        state: FSMContext,
        workers_service: WorkersService):
    print("PROFILE1", query.message.chat.id)

    worker: Worker = await workers_service.repository.get(
        pk=query.message.chat.id
    )

    if callback_data.show_profile:
        await query.bot.edit_message_text(
            text=ACCOUNT_DATA_MESSAGE.format(
                first_name=worker.firstname,
                bank_card_number=worker.bank_card_number or "Здесь карта для выплат!",
                meet_link=worker.meet_link or "А по этой ссылке ученики зайдут на урок!",
                phone_number=worker.phone_number or "Тут будет ваш телефон)",
                desctiption=worker.description or "Описание скоро будет здесь..."
            ),
            message_id=query.message.message_id,
            chat_id=query.message.chat.id,
            reply_markup=get_profile_inline_kb()
        )
    else:
        await query.bot.edit_message_text(
            text=await generate_main_stats_message_text(
                template=START_MESSAGE,
                workers_service=workers_service,
                worker=worker
            ),
            reply_markup=get_home_inline_kb(),
            message_id=query.message.message_id,
            chat_id=query.message.chat.id,
        )


@router.callback_query(UpdateProfileInfoData.filter(
    F.update_field != None
))
async def update_profile_info(
        query: CallbackQuery,
        callback_data: UpdateProfileInfoData,
        state: FSMContext):
    try:
        await state.set_state(
            profile_states.UpdateProfileData.from_callback_data(
                callback_data=callback_data
            )
        )
    except KeyError:
        return await query.bot.send_message(
            chat_id=query.message.chat.id,
            text="❌ Пока невозможно обновить данные"
        )

    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text="☑ Отправьте новое значение"
    )
