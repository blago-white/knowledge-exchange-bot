from aiogram import Router
from aiogram.filters.command import CommandStart, CommandObject
from aiogram.types import Message

from keyboards.inline import get_home_inline_kb
from models.worker import Worker
from services.worker import WorkersService
from ..providers import provide_model_service
from ..replies import START_MESSAGE
from ..common.utils.messages import generate_main_stats_message_text

router = Router(name=__name__)


@router.message(CommandStart())
@provide_model_service(WorkersService)
async def start(message: Message,
                command: CommandObject,
                workers_service: WorkersService):
    is_created, worker = await workers_service.get_or_create(
        username=message.from_user.first_name,
        tag=message.from_user.username
    )

    if is_created:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="✨<b>Рады вас видеть, не забудьте заполнить данные о себе в разделе 'Профиль'!</b>"
        )

    await message.bot.send_message(
        chat_id=message.from_user.id,
        text=await generate_main_stats_message_text(
            workers_service=workers_service,
            worker=worker,
            template=START_MESSAGE
        ),
        reply_markup=get_home_inline_kb(),
    )
