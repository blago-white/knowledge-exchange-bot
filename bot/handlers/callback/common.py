from aiogram import Router, F
from aiogram.types.input_file import InputFile, FSInputFile
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.user import UserService, UserType
from services.worker import WorkersService
from services.student import StudentsService
from keyboards.inline import get_home_inline_kb, get_student_menu_kb
from handlers.providers import provide_model_service

from ..replies import (START_MESSAGE,
                       STUDENT_START_MESSAGE,
                       STUDENT_NEXT_LESSON_LABEL_EMPTY,
                       STUDENT_NEXT_LESSON_LABEL_EXISTS)
from ..common.utils.messages import generate_main_stats_message_text, generate_student_main_message
from .utils.data import ABOUT_INFO_DATA, TO_HOME_DATA

router = Router(name=__name__)


@router.callback_query(F.data == ABOUT_INFO_DATA)
async def show_about(query: CallbackQuery):
    await query.message.bot.send_photo(
        chat_id=query.message.chat.id,
        caption="""<span class="tg-spoiler">Я - Богдан, фулл-стек разработчик на Python с опытом 5 лет\n
В прошлом работал репетитором 2 года, успел поработать в Luxkode, 
но основную часть времени я работал <b>на себя</b>,
это и побудило меня создать универсальную утилиту для оптимизации работы.</span>

Этот бот существует исключительно из - за этого —

<i>1️⃣ Легче получить ученика по 1 клику, чем искать его самому</i>

<i>2️⃣ Легче продать ученика по 1 клику, чем договариваться с покупателем</i>

<i>3️⃣ Легче передать всю работу <b><i>Знания.Про</i></b>, чем самому решать проблемы с коммуникациями</i>

<i>4️⃣ Легче видеть четкую метрику перед глазами, чем расчитывать ее в калькуляторе</i>

<i>5️⃣ Спокойнее когда за сделку отвечает "машина" а не серые персоны</i>

<i>ИНН - <code>312348585325</code></i>
<i>ОГРНИП - <code>323310000063180</code></i>
<i>2025 ИП Логинов Богдан Николаевич, все права на бот и его содержание защищены, 
любое несанкционирование использование контента из бота запрещено!</i>
""",
        photo=FSInputFile(
            "D:\FDISKCOPY\python\knowledge-exchange-bot\\bot\static\iam.jpg"
        ),
    )


@router.callback_query(F.data == TO_HOME_DATA)
@provide_model_service(UserService, WorkersService, StudentsService)
async def go_home_screen(
        query: CallbackQuery,
        user_service: UserService,
        workers_service: WorkersService,
        students_service: StudentsService,
        state: FSMContext):
    await state.clear()

    user_type, user = await user_service.get_user(
        telegram_id=query.message.chat.id
    )

    if user_type == UserType.WORKER:
        await query.bot.edit_message_text(
            text=await generate_main_stats_message_text(
                template=START_MESSAGE,
                workers_service=workers_service,
                worker=user
            ),
            reply_markup=get_home_inline_kb(),
            message_id=query.message.message_id,
            chat_id=query.message.chat.id,
        )
    else:
        students_service.student_id = query.message.chat.id

        nearest_lesson = await students_service.get_nearest_lesson()

        await query.bot.edit_message_text(
            text=generate_student_main_message(
                template=STUDENT_START_MESSAGE,
                next_lesson_template=STUDENT_NEXT_LESSON_LABEL_EXISTS
                if nearest_lesson else
                STUDENT_NEXT_LESSON_LABEL_EMPTY,
                next_lesson=nearest_lesson,
                student=user,
                meet_link=nearest_lesson.subject.worker.meet_link if nearest_lesson else ""
            ),
            reply_markup=get_student_menu_kb(),
            message_id=query.message.message_id,
            chat_id=query.message.chat.id,
        )
