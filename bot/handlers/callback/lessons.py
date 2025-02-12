from aiogram import F
from aiogram.filters import and_f
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import (ReplyKeyboardRemove,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup)

from keyboards.inline import (get_lesson_data_inline_kb,
                              get_lesson_commiting_kb,
                              get_subject_lessons_kb,
                              get_edit_lesson_kb)
from models.lesson import Lesson
from services.lesson import LessonsService
from services.exceptions.lessons import (CompliteLessonDateUncorrect,
                                         StudentBalanceEmpty)
from handlers.states import lessons as lessons_states

from ..callback.utils import data
from ..common.utils.messages import generate_lesson_data_message_text
from ..providers import provide_model_service
from ..replies import LESSON_DATA_MESSAGE

router = Router(name=__name__)


def update_drop_lessons_kb(keyboard: list[list[InlineKeyboardButton]]):
    for row_n, row in enumerate(keyboard):
        for i_n, i in enumerate(row):
            if "lesson-drop" in i.callback_data:
                keyboard[row_n][i_n].text = "⛔ Удалить урок (-и)" \
                    if i.text == "❎ Готово" \
                    else "❎ Готово"
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
            return await query.answer("⚠ Невозможно удалить ⚠")
        else:
            return await query.answer(text="✅ Удалили! ✅")

    try:
        worker_id = (callback_data.seller_id
            if callback_data.seller_view
            else query.message.chat.id)

        print("ABCD", worker_id, callback_data.seller_id, query.message.chat.id)

        lesson: Lesson = await lessons_service.retrieve(
            worker_id=worker_id
        )
    except Exception as e:
        print(e)
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
        reply_markup=get_lesson_data_inline_kb(
            subject_id=lesson.subject_id,
            lesson_id=lesson.id,
            seller_view=callback_data.seller_view
        )
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

    match action:
        case "commit_lesson":
            try:
                factor = dict(await state.get_data()).get("factor", 1)

                await lessons_service.repository.bulk_create_lessons(
                    lesson_data=dict(
                        date=data_.get("datetime"),
                        duration=data_.get("duration"),
                        is_free=data_.get("is_free", False),
                        subject_id=data_.get("subject_id")
                    ),
                    copies=int(factor)
                )
            except Exception as e:
                print(e)
                return await query.message.edit_text(
                    text="⭕ <b>Ошибка создания урока, обратитесь в поддержку!</b>")

            await query.message.edit_reply_markup()

            await query.message.edit_text(
                text="✅ <b>Урок создан</b>",
            )

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
            await query.answer(f"Повторили урок {callback_data.schedule_factor} раз.")

            await state.set_data(data=(await state.get_data()) | {
                "factor": callback_data.schedule_factor
            })

            await query.message.edit_reply_markup(
                reply_markup=get_lesson_commiting_kb(
                    is_free=data_.get("is_free"),
                    is_scheduled=True
                )
            )


@router.callback_query(data.DropLessonData.filter(F.many == True))
async def drop_lesson_bulk(
        query: CallbackQuery,
        callback_data: data.DropLessonData,
        state: FSMContext):
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

        try:
            await query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=updated_kb)
            )
        except:
            pass

        await state.set_state(lessons_states.DropLessonsForm.drop_lesson)


@router.callback_query(
    and_f(
        data.DropLessonData.filter(F.many == False),
        data.DropLessonData.filter(F.lesson_id != None)
    )
)
@provide_model_service(LessonsService)
async def drop_lesson_datailed(
        query: CallbackQuery,
        callback_data: data.DropLessonData,
        state: FSMContext,
        lessons_service: LessonsService):
    lessons_service.lesson_id = callback_data.lesson_id

    try:
        await lessons_service.drop(worker_id=query.message.chat.id)
    except:
        return await query.answer("⚠ Невозможно удалить ⚠")
    else:
        await query.answer("✅ Удалили! ✅")


@router.callback_query(data.LessonCompliteData.filter())
@provide_model_service(LessonsService)
async def complete_lesson(
        query: CallbackQuery,
        callback_data: data.LessonCompliteData,
        state: FSMContext,
        lessons_service: LessonsService):
    lessons_service.lesson_id = callback_data.lesson_id

    bot, chat_id = query.bot, query.message.chat.id

    try:
        result = await lessons_service.complete_lesson(
            worker_id=chat_id
        )
    except CompliteLessonDateUncorrect:
        return await query.answer("⚠ Время урока еще не подошло ⚠")
    except PermissionError:
        return await query.answer("⚠ Кажется у вас нет прав ⚠")
    except StudentBalanceEmpty:
        await query.answer()

        await query.bot.send_message(
            chat_id=chat_id,
            text="⚠ <b>У ученика не осталось баланса</b>\n\n"
                 "Урок провести не получится, "
                 "либо сделайте урок бесплатным, либо свяжитесь с учеником!"
        )

        return
    except Exception as e:
        return await query.answer("Что-то пошло не так, напишите в поддержку")
    else:
        await query.answer()

    try:
        await bot.send_message(
            chat_id=result.subject.student_id,
            text="🔆 <b>Вы посетили еще один урок</b>\n"
                 "Двигайтесь в том же "
                 "темпе и вы достигните всех целей!\n"
                 "<i>При любых вопросах пишите в поддержку - /support</i>"
        )
    except:
        pass

    if result.for_paid and result.offer:
        await bot.send_message(
            chat_id=result.seller_id,
            text="💸 <b>Новое поступление по проданному ученику</b>\n"
                 f"Предмет — {result.subject.title}\n"
                 f"Ученик — {result.subject.student.name} | "
                 f"{result.subject.student.city}\n"
                 f"<b>{result.offer.paid_sum}₽ / {result.offer.cost}₽</b>\n"
        )

        if result.paid_total_now:
            await bot.send_message(
                chat_id=chat_id,
                text="✨ <b>Вы полностью выплатили ученика теперь можно "
                     "его продавать и получить контакты!</b>"
            )

            await bot.send_message(
                chat_id=result.seller_id,
                text="🔥 <b>Ученик полностью оплачен!</b>"
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text="⭐ <b>Вы оплатили еще часть!</b>"
            )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="🔆 <b>Поздравляем с еще одним проведенным уроком!</b>"
        )

    if result.low_balance_student:
        await bot.send_message(
            chat_id=result.subject.student_id,
            text="📛 <b>Видим, что у вас заканчивается баланс</b>\n"
                 "До следующего урока постарайтесь внести оплату, <b>спасибо</b>🤍!"
        )

        await bot.send_message(
            chat_id=chat_id,
            text="📛 <b>У ученика не осталось баланса на следующие уроки!</b>"
        )


@router.callback_query(data.EditLessonData.filter())
async def edit_lesson(
        query: CallbackQuery,
        callback_data: data.EditLessonData,
        state: FSMContext):
    await query.answer()

    if callback_data.open_menu:
        return await query.message.edit_reply_markup(
            reply_markup=get_edit_lesson_kb(
                lesson_id=callback_data.lesson_id,
                subject_id=callback_data.subject_id
            )
        )

    elif callback_data.edit_record_link:
        await state.set_state(state=lessons_states.EditLessonDataForm().edit_record_link)

        await query.message.bot.send_message(
            chat_id=query.message.chat.id,
            text="🎥 Введите ссылку на запись:"
        )

    elif callback_data.edit_date:
        await state.set_state(state=lessons_states.EditLessonDataForm().edit_datetime)

        await query.message.bot.send_message(
            chat_id=query.message.chat.id,
            text="📆 Введите новую дату и время:"
        )

    await state.set_data(data=dict(lesson_id=callback_data.lesson_id))
