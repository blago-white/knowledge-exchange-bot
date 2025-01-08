from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline import get_home_inline_kb, get_profile_inline_kb
from repositories.workers import WorkersRepository
from models.worker import Worker

from ..callback.utils.data import RenderProfileData
from ..replies import ACCOUNT_DATA_MESSAGE, START_MESSAGE
from ..providers import provide_model_repository


router = Router(name=__name__)


@router.callback_query(RenderProfileData.filter(
    F.show_profile != None
))
@provide_model_repository(WorkersRepository)
async def render_profile(
        query: CallbackQuery,
        callback_data: CallbackData,
        state: FSMContext,
        workers_repository: WorkersRepository):
    if callback_data.show_profile:
        worker: Worker = await workers_repository.get(pk=query.message.chat.id)

        await query.bot.edit_message_text(
            text=ACCOUNT_DATA_MESSAGE.format(
                first_name=worker.firstname,
                bank_card_number=worker.bank_card_number,
                meet_link=worker.meet_link,
                phone_number=worker.phone_number,
                desctiption=worker.description
            ),
            message_id=query.message.message_id,
            chat_id=query.message.chat.id,
            reply_markup=get_profile_inline_kb()
        )
    else:
        await query.bot.edit_message_text(
            text=START_MESSAGE.format(
                user_id=query.message.chat.id,
                selled_students=39,
                week_profit="40.500",
                total_profit="210.450",
                referals_count=9,
                meet_link="https://meet.google.com/xkf"
            ),
            reply_markup=get_home_inline_kb(),
            message_id=query.message.message_id,
            chat_id=query.message.chat.id,
        )
