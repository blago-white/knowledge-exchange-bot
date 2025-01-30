from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import (get_home_inline_kb,
                              get_profile_inline_kb,
                              get_subjects_table_kb,
                              get_subject_details_kb,
                              get_subject_lessons_kb)
from models.worker import Worker
from services.lesson import SubjectsService, Subject
from services.worker import WorkersService
from ..callback.utils.data import (RenderProfileData,
                                   UpdateProfileInfoData,
                                   GetWorkerSubjectsData,
                                   TO_HOME_DATA,
                                   StudentProfileData,
                                   GetSubjectLessonsData)
from ..common.utils.messages import generate_main_stats_message_text
from ..providers import provide_model_service
from ..replies import ACCOUNT_DATA_MESSAGE, START_MESSAGE
from ..states import profile as profile_states

router = Router(name=__name__)


@router.callback_query(RenderProfileData.filter(
    F.show_profile != None
))
@provide_model_service(WorkersService)
async def render_profile(
        query: CallbackQuery,
        callback_data: CallbackData,
        state: FSMContext,
        workers_service: WorkersService):
    worker: Worker = await workers_service.repository.get(
        pk=query.message.chat.id
    )

    await query.bot.edit_message_text(
        text=ACCOUNT_DATA_MESSAGE.format(
            first_name=worker.firstname,
            bank_card_number=worker.bank_card_number or "Здесь карта для выплат!",
            meet_link=worker.meet_link or "А по этой ссылке ученики зайдут на урок!",
            phone_number=worker.phone_number or "Тут будет ваш телефон)",
            desctiption=worker.description or "Описание скоро будет здесь..."
        ),
        message_id=query.message.message_id,
        chat_id=query.message.chat.id,
        reply_markup=get_profile_inline_kb()
    )


@router.callback_query(F.data == TO_HOME_DATA)
@provide_model_service(WorkersService)
async def go_home_screen(
        query: CallbackQuery,
        workers_service: WorkersService):
    worker: Worker = await workers_service.repository.get(
        pk=query.message.chat.id
    )

    await query.bot.edit_message_text(
        text=await generate_main_stats_message_text(
            template=START_MESSAGE,
            workers_service=workers_service,
            worker=worker
        ),
        reply_markup=get_home_inline_kb(),
        message_id=query.message.message_id,
        chat_id=query.message.chat.id,
    )


@router.callback_query(UpdateProfileInfoData.filter(
    F.update_field != None
))
async def update_profile_info(
        query: CallbackQuery,
        callback_data: UpdateProfileInfoData,
        state: FSMContext):
    await query.answer()

    try:
        await state.set_state(
            profile_states.UpdateProfileData.from_callback_data(
                callback_data=callback_data
            )
        )
    except KeyError:
        return await query.bot.send_message(
            chat_id=query.message.chat.id,
            text="❌ Пока невозможно обновить данные"
        )

    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text="☑ Отправьте новое значение"
    )


@router.callback_query(GetWorkerSubjectsData.filter(
    F.filter != None
))
@provide_model_service(SubjectsService)
async def update_profile_info(
        query: CallbackQuery,
        callback_data: UpdateProfileInfoData,
        state: FSMContext,
        subjects_service: SubjectsService):
    await query.answer()

    subjects: list[
        Subject] = await subjects_service.repository.get_all_for_worker(
        worker_id=query.message.chat.id
    )

    if not subjects or not len(subjects):
        return await query.message.edit_text(
            text="👌 <b>У вас еще нет учеников, но скоро они обязательно появятся:)</b>",
            reply_markup=get_subjects_table_kb(subjects=subjects)
        )

    await query.message.edit_text(
        text="📕 <b>Тут все ваши ученики:</b>",
        reply_markup=get_subjects_table_kb(
            subjects=subjects
        )
    )


@router.callback_query(StudentProfileData.filter(
    F.subject_id != None
))
@provide_model_service(SubjectsService)
async def show_subject_profile(
        query: CallbackQuery,
        callback_data: StudentProfileData,
        state: FSMContext,
        subjects_service: SubjectsService):
    subjects_service.subject_id = callback_data.subject_id

    try:
        subject: Subject = await subjects_service.retrieve(
            worker_id=query.message.chat.id
        )
    except Exception as e:
        return await query.answer(
            "Вы не можете просмотреть профиль этого ученика!")
    else:
        await query.answer()

    await query.message.edit_text(
        text=f"📍 <b>{subject.student.name} [{subject.student.city}]</b>\n"
             f"📕 Предмет — <i>{subject.title}\n"
             f"🕑 Ставка — {subject.rate}₽/ч</i>\n"
             f"👤 О ученике — <i>{
             subject.student.description or 'пока ничего не известно('
             }</i>\n\n"
             f"<i>{
             "— " + (subject.description or "Кажется, заметок еще нет!")
             }</i>",
        reply_markup=get_subject_details_kb(subject=subject)
    )


@router.callback_query(GetSubjectLessonsData.filter(
    F.subject_id != None
))
@provide_model_service(SubjectsService)
async def show_subject_lessons(
        query: CallbackQuery,
        callback_data: GetSubjectLessonsData,
        state: FSMContext,
        subjects_service: SubjectsService):
    if callback_data.only_show_legend:
        return await query.answer(
            "!ВРЕМЯ-МСК!\n"
            "☑ — Урок запланирован\n"
            "⁉ — Урок уже должен был начаться\n"
        )

    subjects_service.subject_id = callback_data.subject_id

    try:
        lessons = await subjects_service.get_lessons(
            worker_id=query.message.chat.id
        )
    except Exception as e:
        return await query.answer("Вы не можете просмотреть уроки!")

    if not lessons:
        await query.answer("Уроков еще не было, исправляйте:)")
    else:
        await query.answer()

    await query.message.edit_reply_markup(
        reply_markup=get_subject_lessons_kb(
            subject_id=callback_data.subject_id,
            lessons=lessons
        )
    )
