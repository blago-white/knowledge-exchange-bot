from aiogram import Router
from aiogram.filters.command import CommandStart, CommandObject, Command
from aiogram.types import Message

from keyboards.inline import get_home_inline_kb, get_student_menu_kb
from models.worker import Worker
from services.worker import WorkersService
from services.user import UserService, UserType
from services.student import StudentsService
from ..providers import provide_model_service
from ..replies import START_MESSAGE, STUDENT_START_MESSAGE, STUDENT_NEXT_LESSON_LABEL_EMPTY, STUDENT_NEXT_LESSON_LABEL_EXISTS
from ..common.utils.messages import (generate_main_stats_message_text,
                                     generate_student_main_message)

router = Router(name=__name__)


@router.message(CommandStart())
@provide_model_service(WorkersService,
                       StudentsService,
                       UserService)
async def start(message: Message,
                command: CommandObject,
                workers_service: WorkersService,
                students_service: StudentsService,
                user_service: UserService):
    user_type, user = await user_service.get_user(telegram_id=message.chat.id)

    if (command.args and
            user_type == UserType.UNKNOWN and
            ("student" in command.args)):
        try:
            student_ref_token = command.args.replace(
                " ", ""
            ).split("=")[-1]

            if not student_ref_token:
                raise Exception
        except:
            return await message.reply("❌ Вам была дана некорректная ссылка!")

        students_service.telegram_id = message.chat.id

        token = await students_service.ref_token_exists(ref_token=student_ref_token)

        if not token:
            return await message.reply("😶 Не находим вас, уточните ссылку у вашего учителя...")

        students_service.student_id = token.student_id

        try:
            await students_service.connect_student_telegram()
        except:
            return await message.reply("😄 Кажется вы уже зарегистрированы")

        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"🔰 Рады вас видеть, {message.from_user.first_name} — /start"
        )
    elif user_type == UserType.STUDENT:
        students_service.student_id = message.chat.id
        next_lesson = await students_service.get_nearest_lesson()

        print(next_lesson, type(next_lesson))

        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=generate_student_main_message(
                next_lesson=next_lesson,
                next_lesson_template=STUDENT_NEXT_LESSON_LABEL_EXISTS if next_lesson else STUDENT_NEXT_LESSON_LABEL_EMPTY,
                student=user,
                template=STUDENT_START_MESSAGE,
                meet_link=next_lesson.subject.worker.meet_link if next_lesson else None
            ),
            reply_markup=get_student_menu_kb()
        )
    # elif user_type == UserType.UNKNOWN:
    #     await message.bot.send_message(
    #         chat_id=message.chat.id,
    #         text="⭐Рады видеть вас, вы репетитор?",
    #         reply_markup=...
    #     )
    elif user_type in (UserType.UNKNOWN, UserType.WORKER):
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


@router.message(Command("support"))
async def get_support(message: Message):
    await message.bot.send_message(
        chat_id=message.chat.id,
        text="📝 <b>При любых вопросах/предложениях/если "
             "нашли ошибку - @VictorMerinov</b>\n\n"
             "<i>🕘 Работаем с 12:00 до 23:59</i>"
    )
