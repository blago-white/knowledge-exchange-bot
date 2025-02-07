import datetime as dt

from aiogram import F
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.lesson import LessonsService, Lesson
from keyboards.inline import get_lesson_commiting_kb, get_lesson_data_inline_kb
from handlers.states import lessons as lessons_states
from handlers.common.validators import datetime, links
from handlers.common.utils.messages import generate_lesson_data_message_text
from handlers.replies import LESSON_DATA_MESSAGE
from handlers.providers import provide_model_service

from handlers.callback.lessons import show_lesson

router = Router(name=__name__)


@router.message(lessons_states.LessonCreationForm.add_datetime)
async def add_lesson_datetime(
        message: Message,
        state: FSMContext):
    try:
        validated_dt = datetime.get_datetime_validated(input_date=message.text)
    except ValueError as validation_error:
        return await message.reply(
            text=f"❌{str(validation_error)}\n\n<i>Попробуйте еще разок!</i>"
        )
    except Exception as e:
        print(f"EXCEPTION add_lesson_datetime: {e!r} {e}")
        return await message.reply(
            text=f"❌Что-то пошло не так...\n\n<i>Попробуйте еще разок!</i>"
        )

    current_data = await state.get_data()

    await state.set_data(data=current_data | dict(datetime=validated_dt))

    await state.set_state(lessons_states.LessonCreationForm.add_duration)

    await message.reply("✅ <b>Так и запишем!</b>")

    await message.bot.send_message(chat_id=message.chat.id,
                                   text="⏳ <b>И длительность урока:</b>")


@router.message(lessons_states.LessonCreationForm.add_duration)
async def add_lesson_datetime(
        message: Message,
        state: FSMContext):
    try:
        duration = datetime.get_validated_duration(duration_input=message.text)
    except ValueError as validation_error:
        return await message.reply(
            text=f"❌{str(validation_error)}\n\n<i>Попробуйте еще разок!</i>"
        )
    except:
        return await message.reply(
            text=f"❌Что-то пошло не так...\n\n<i>Попробуйте еще разок!</i>"
        )

    current_data = await state.get_data()

    datetime_: dt.datetime = current_data.get("datetime")

    await state.set_data(data=current_data | dict(duration=duration))

    await state.set_state()

    await message.bot.send_message(
        chat_id=message.chat.id,
        text="✨ <b>Пока отлично, если надо — выберите опции, и нажмите добавить</b>"
    )

    await message.bot.send_message(
        chat_id=message.chat.id,
        text="✔ Вот что выходит:\n"
             f"Дата — <b>{datetime_.strftime(format="%d.%m %H:%M")}</b>\n"
             f"Длительность — <b>{duration}мин.</b>",
        reply_markup=get_lesson_commiting_kb()
    )


@router.message(lessons_states.EditLessonDataForm.edit_record_link)
@router.message(lessons_states.EditLessonDataForm.edit_datetime)
@provide_model_service(LessonsService)
async def edit_lesson(
        message: Message,
        state: FSMContext,
        lessons_service: LessonsService):
    lesson_id = (await state.get_data()).get("lesson_id")
    lessons_service.lesson_id = int(lesson_id)

    state_ = await state.get_state()

    if state_ == lessons_states.EditLessonDataForm.edit_datetime:
        response = await edit_lesson_date(
            message=message,
            state=state,
            lessons_service=lessons_service
        )
    else:
        response = await edit_record_link(
            message=message,
            state=state,
            lessons_service=lessons_service
        )

    if type(response) is Lesson:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=generate_lesson_data_message_text(
                template=LESSON_DATA_MESSAGE,
                lesson=response
            ),
            reply_markup=get_lesson_data_inline_kb(
                subject_id=response.subject_id,
                lesson_id=response.id
            )
        )


async def edit_record_link(
        message: Message,
        state: FSMContext,
        lessons_service: LessonsService):
    try:
        validated_record = links.get_validated_link(link_input=message.text)
    except ValueError as validation_error:
        return await message.reply(
            text=f"❌{str(validation_error)}\n\n<i>Попробуйте еще разок!</i>"
        )
    except:
        return await message.reply(
            text=f"❌Что-то пошло не так...\n\n<i>Попробуйте еще разок!</i>"
        )

    try:
        lesson = await lessons_service.update(worker_id=message.chat.id,
                                              record_link=validated_record)
    except:
        return await message.reply(
            "❌ Невозможно добавить запись, напишите-ка в поддержку")

    await message.reply("✅ <b>Спасибо, это интересно!</b>")
    await state.clear()

    return lesson


async def edit_lesson_date(
        message: Message,
        state: FSMContext,
        lessons_service: LessonsService):
    try:
        validated_datetime = datetime.get_datetime_validated(
            input_date=message.text
        )
    except ValueError as validation_error:
        return await message.reply(
            text=f"❌{str(validation_error)}\n\n<i>Попробуйте еще разок!</i>"
        )
    except:
        return await message.reply(
            text=f"❌Что-то пошло не так...\n\n<i>Попробуйте еще разок!</i>"
        )

    try:
        lesson = await lessons_service.update(worker_id=message.chat.id,
                                              date=validated_datetime)
    except Exception as e:
        return await message.reply(
            "❌ Невозможно добавить запись, напишите-ка в поддержку")

    await message.reply(
        "✅ <b>Действительно, в этот время удобнее, записали!</b>")

    await state.clear()

    return lesson
