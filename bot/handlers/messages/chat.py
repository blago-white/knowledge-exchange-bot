from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReactionTypeEmoji

from services.dialog import DialogsService
from services.user import UserType
from models.dialog import Message as Message_
from keyboards import inline

from ..providers import provide_model_service
from ..states.chat import CHATTING


router = Router(name=__name__)


@router.message(Command("stop"))
async def stop_messaging(message: Message, state: FSMContext):
    await state.clear()
    await message.reply("✅ <b>Вы завершили отправку сообщений</b>")


@router.message(CHATTING)
@provide_model_service(DialogsService)
async def enter_message(message: Message,
                        state: FSMContext,
                        dialogs_service: DialogsService):
    data = dict(await state.get_data())
    sender_type = data.get("sender_type")

    print("DDD", sender_type)

    try:
        saved_message: Message_ = await dialogs_service.add_message(
            sender_id=message.chat.id,
            message=Message_(
                id=message.message_id,
                subject_id=data.get("subject_id"),
                sender=sender_type,
                text=message.text,
            )
        )
    except Exception as e:
        print(e)
        return

    recipient_id = saved_message.subject.student.telegram_id \
        if sender_type == str(UserType.WORKER) \
        else saved_message.subject.worker_id

    if sender_type == str(UserType.STUDENT):
        user = saved_message.subject.student
        username = f"{user.name} | {user.city} [{saved_message.subject.title}]"
    else:
        user = saved_message.subject.worker
        username = f"{user.firstname}{(" " + user.lastname) or ""} [{saved_message.subject.title}]"

    await message.react(reaction=[ReactionTypeEmoji(emoji="👌")])

    await message.bot.send_message(
        **dict(
            chat_id=recipient_id,
            text=f"<i>{saved_message.text}</i>"
                 f"\n\n💬 [Для поиска: <code>#{saved_message.subject_id}</code>] "
                 f"<b>Сообщение от {
                    "ученика" if sender_type == str(UserType.STUDENT) else "репетитора"
                 } — {username}</b>",
            reply_markup=inline.get_chat_message_reply_kb(
                subject_id=saved_message.subject_id,
                parent_msg_id=message.message_id,
                recipient_id=message.chat.id
            )
        ) | (dict(reply_to_message_id=data.get("parent_msg_id")) if data.get("parent_msg_id") else {})
    )
