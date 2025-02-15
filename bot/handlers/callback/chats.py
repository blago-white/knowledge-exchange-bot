from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.dialog import Message, DialogsService
from services.student import Student, StudentsService
from services.user import UserService, UserType
from keyboards.inline import get_chats_keyboard
from handlers.common.utils.messages import generate_dialog_history_message

from ..providers import provide_model_service
from .utils import data


router = Router(name=__name__)


@router.callback_query(data.MyChatsListData.filter())
@provide_model_service(DialogsService, UserService)
async def show_chats_list(query: CallbackQuery,
                          callback_data: data.MyChatsListData,
                          dialogs_service: DialogsService,
                          user_service: UserService):
    await query.answer()

    user_type, user = await user_service.get_user(telegram_id=query.message.chat.id)

    previews = await dialogs_service.show_all_chats(
        user_type=user_type,
        user=user
    )

    if not previews:
        return await query.message.edit_text(
            text="💬 <b>Чатов еще не было!</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=data.TO_HOME_DATA
            )]])
        )

    return await query.message.edit_text(
        text="💬 <b>Здесь все чаты: </b>",
        reply_markup=get_chats_keyboard(previews=previews)
    )


@router.callback_query(data.SendMessageData.filter())
@provide_model_service(DialogsService, UserService)
async def send_message(query: CallbackQuery,
                       state: FSMContext,
                       callback_data: data.SendMessageData,
                       dialogs_service: DialogsService,
                       user_service: UserService):
    await query.answer()

    user_type, user = await user_service.get_user(
        telegram_id=query.message.chat.id
    )

    if (not callback_data.recipient_id) and (user_type == UserType.WORKER):
        return await query.answer("📛 Нельзя отправить сообщение")

    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text="Вводите сообщения, а когда закончите - отправьте /stop"
    )

    await state.set_data(data=dict(
        sender_type=str(user_type),
        subject_id=callback_data.subject_id,
        parent_msg_id=callback_data.parent_msg_id if callback_data.parent_msg_id else None
    ))


@router.callback_query(data.OpenChatData.filter())
@provide_model_service(DialogsService, UserService)
async def open_chat(query: CallbackQuery,
                    callback_data: data.OpenChatData,
                    dialogs_service: DialogsService,
                    user_service: UserService):
    dialog = await dialogs_service.get_messages(
        subject_id=callback_data.subject_id
    )

    user_type, _ = await user_service.get_user(
        telegram_id=query.message.chat.id
    )

    await query.message.edit_text(
        text=generate_dialog_history_message(dialog=dialog, self_type=user_type),
        reply_markup=query.message.reply_markup
    )
