import datetime as dt

from aiogram import F
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_lesson_commiting_kb

from handlers.states import lessons as lessons_states

from handlers.common.validators import datetime


router = Router(name=__name__)


@router.message(lessons_states.LessonCreationForm.add_datetime)
async def add_lesson_datetime(message: Message,
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
async def add_lesson_datetime(message: Message,
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
