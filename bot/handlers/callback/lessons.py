from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import (ReplyKeyboardRemove,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup)

from keyboards.inline import (get_lesson_data_inline_kb,
                              get_lesson_commiting_kb,
                              get_subject_lessons_kb)
from models.lesson import Lesson
from services.lesson import LessonsService

from ..callback.utils import data
from ..common.utils.messages import generate_lesson_data_message_text
from ..providers import provide_model_service
from ..replies import LESSON_DATA_MESSAGE
from handlers.states import lessons as lessons_states

router = Router(name=__name__)


def update_drop_lessons_kb(keyboard: list[list[InlineKeyboardButton]]):
    for row_n, row in enumerate(keyboard):
        for i_n, i in enumerate(row):
            if i.callback_data == data.DropLessonData().pack():
                keyboard[row_n][i_n].text = "⛔ Удалить урок (-и)" if i.text == "❎ Готово" else "❎ Готово"
                break

    return keyboard


@router.callback_query(data.ShowLessonInfoData.filter(
    F.lesson_id != None
))
@provide_model_service(LessonsService)
async def show_lesson(
        query: CallbackQuery,
        callback_data: data.ShowLessonInfoData,
        state: FSMContext,
        lessons_service: LessonsService):
    lessons_service.lesson_id = callback_data.lesson_id

    state_ = await state.get_state()

    if state_ == lessons_states.DropLessonsForm.drop_lesson:
        try:
            await lessons_service.drop(worker_id=query.message.chat.id)
        except Exception as e:
            print(repr(e), e)
            return await query.answer("⚠ Невозможно удалить ⚠")
        else:
            return await query.answer(text="✅ Удалили! ✅")

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


@router.callback_query(data.AddLessonData.filter())
async def add_lesson(
        query: CallbackQuery,
        callback_data: data.AddLessonData,
        state: FSMContext):
    await query.answer()

    await state.set_state(state=lessons_states.LessonCreationForm.add_datetime)
    await state.set_data(data=dict(subject_id=callback_data.subject_id))

    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text="⏰ <b>Когда будете заниматься?</b>\n\n"
             "<i>Формыт даты и времени, используйте его: 31.01 12:30</i>"
    )


@router.callback_query(data.LessonCommitViewCallbackData.filter())
@provide_model_service(LessonsService)
async def lesson_creation_form_action(
        query: CallbackQuery,
        callback_data: data.LessonCommitViewCallbackData,
        state: FSMContext,
        lessons_service: LessonsService):
    action = [i for i in dir(callback_data) if i[0] != "_" and (getattr(callback_data, i) is True)].pop()

    data_: dict = await state.get_data()

    print(f"ACTION: {action}")

    match action:
        case "commit_lesson":
            try:
                await lessons_service.repository.create(
                    lesson_data=Lesson(
                        date=data_.get("datetime"),
                        duration=data_.get("duration"),
                        is_free=data_.get("is_free", False),
                        subject_id=data_.get("subject_id")
                    )
                )
            except:
                return await query.message.edit_text(
                    text="⭕ <b>Ошибка создания урока, обратитесь в поддержку!</b>",
                    reply_markup=ReplyKeyboardRemove
                )

            await query.message.edit_text(
                text="✅ <b>Урок создан</b>",
            )

            await query.message.edit_reply_markup()

        case "make_free":
            await state.set_data(
                data=data_ | dict(is_free=not data_.get("is_free"))
            )

            await query.message.edit_reply_markup(
                reply_markup=get_lesson_commiting_kb(
                    is_free=not data_.get("is_free"),
                    is_scheduled=data_.get("is_scheduled")
                )
            )

        case "make_scheduled":
            await query.answer("Скоро будет...")
            await query.message.edit_reply_markup(
                reply_markup=get_lesson_commiting_kb(
                    is_free=data_.get("is_free"),
                    is_scheduled=data_.get("is_scheduled")
                )
            )


@router.callback_query(data.DropLessonData.filter())
@provide_model_service(LessonsService)
async def drop_lesson(
        query: CallbackQuery,
        callback_data: data.LessonCommitViewCallbackData,
        state: FSMContext,
        lessons_service: LessonsService):
    state_ = await state.get_state()

    if state_ == lessons_states.DropLessonsForm.drop_lesson:
        updated_kb = update_drop_lessons_kb(
            keyboard=query.message.reply_markup.inline_keyboard
        )

        await query.answer("Удалили, перезайдите и увидите!")

        await query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(inline_keyboard=updated_kb)
        )

        await state.clear()
    else:
        updated_kb = update_drop_lessons_kb(
            keyboard=query.message.reply_markup.inline_keyboard
        )

        await query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(inline_keyboard=updated_kb)
        )

        await state.set_state(lessons_states.DropLessonsForm.drop_lesson)
