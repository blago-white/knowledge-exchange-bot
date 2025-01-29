from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import (get_lesson_data_inline_kb)
from models.lesson import Lesson
from services.lesson import LessonsService
from ..callback.utils.data import (ShowLessonInfoData)
from ..common.utils.messages import generate_lesson_data_message_text
from ..providers import provide_model_service
from ..replies import LESSON_DATA_MESSAGE

router = Router(name=__name__)


@router.callback_query(ShowLessonInfoData.filter(
    F.lesson_id != None
))
@provide_model_service(LessonsService)
async def show_lesson(
        query: CallbackQuery,
        callback_data: ShowLessonInfoData,
        state: FSMContext,
        lessons_service: LessonsService):
    lessons_service.lesson_id = callback_data.lesson_id

    try:
        lesson: Lesson = await lessons_service.retrieve(
            worker_id=query.message.chat.id
        )
    except:
        return await query.answer("Нельзя просмотреть этот урок!")
    else:
        await query.answer()

    await query.bot.edit_message_text(
        text=generate_lesson_data_message_text(
            template=LESSON_DATA_MESSAGE,
            lesson=lesson
        ),
        message_id=query.message.message_id,
        chat_id=query.message.chat.id,
        reply_markup=get_lesson_data_inline_kb(subject_id=lesson.subject_id)
    )
