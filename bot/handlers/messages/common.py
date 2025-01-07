from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart, CommandObject

from ..replies import START_MESSAGE
from keyboards.inline import get_home_inline_kb


router = Router(name=__name__)


@router.message(CommandStart())
async def start(message: Message,
                command: CommandObject):
    args = command.args

    print(command.args, command.text)

    await message.bot.send_message(
        chat_id=message.from_user.id,
        text=START_MESSAGE.format(
            user_id=message.chat.id,
            selled_students=39,
            week_profit="40.500",
            total_profit="210.450",
            referals_count=9,
            meet_link="https://meet.google.com/xkf"
        ),
        reply_markup=get_home_inline_kb(),
    )
