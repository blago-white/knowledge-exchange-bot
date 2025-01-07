from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline import get_home_inline_kb, get_profile_inline_kb

from ..callback.utils.data import RenderProfileData
from ..replies import ACCOUNT_DATA_MESSAGE, START_MESSAGE


router = Router(name=__name__)


@router.callback_query(RenderProfileData.filter(
    F.show_profile != None
))
async def render_profile(
        query: CallbackQuery,
        callback_data: CallbackData,
        state: FSMContext):
    print("CALLBACK CATCHED")
    if callback_data.show_profile:
        await query.bot.edit_message_text(
            text=ACCOUNT_DATA_MESSAGE.format(
                first_name="Ivan",
                bank_card_number="1111222233334444",
                meet_link="https://google.com",
                phone_number="+79952481752",
                desctiption="Преподаю python уже более 4х лет, "
                            "Предпочитаю веб разработку, DevOPS, подготавливаю к ЕГЭ"
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
