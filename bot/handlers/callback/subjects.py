from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F

from services.lesson import Subject, SubjectsService
from handlers.callback.utils import data
from keyboards.inline import get_subject_details_kb, get_subject_edit_kb
from handlers.states.subjects import EditSubjectForm

from ..providers import provide_model_service


router = Router(name=__name__)


def update_subject_kb(kb: list):
    for row_n, row in enumerate(keyboard):
        for i_n, i in enumerate(row):
            if "lesson-drop" in i.callback_data:
                keyboard[row_n][i_n].text = "⛔ Удалить урок (-и)" \
                    if i.text == "❎ Готово" \
                    else "❎ Готово"
                break

    return keyboard


@router.callback_query(data.StopSubjectData.filter(F.subject_id != None))
@provide_model_service(SubjectsService)
async def subject_deactivate(
        query: CallbackQuery,
        callback_data: data.StopSubjectData,
        state: FSMContext,
        subjects_service: SubjectsService
):
    subjects_service.subject_id = callback_data.subject_id

    try:
        subject = await subjects_service.invert_active_status(
            worker_id=query.message.chat.id
        )
    except:
        return await query.answer("Что-то пошло не так!")
    else:
        await query.message.edit_reply_markup(
            reply_markup=get_subject_details_kb(
                subject=subject, seller_view=False
            )
        )

    return await query.answer("Готово!")


@router.callback_query(data.EditSubjectData.filter())
async def edit_subject(
        query: CallbackQuery,
        callback_data: data.EditSubjectData,
        state: FSMContext):
    if callback_data.open_menu:
        return await query.message.edit_reply_markup(
            reply_markup=get_subject_edit_kb(
                subject_id=callback_data.subject_id
            )
        )

    reactor = {
        data.SubjectEditField.TITLE: _react_title,
        data.SubjectEditField.DESCRIPTION: _react_description,
        data.SubjectEditField.RATE: _react_rate
    }[callback_data.edit_field]

    await state.set_data(data={
        "field": callback_data.edit_field,
        "subject_id": callback_data.subject_id
    })

    await state.set_state(EditSubjectForm.edit_field)

    await reactor(state=state, query=query)


async def _react_title(state: FSMContext, query: CallbackQuery):
    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text="<b>🔖 Введите новое название</b>"
    )


async def _react_rate(state: FSMContext, query: CallbackQuery):
    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text="<b>🕑 Введите новую ставку за предмет</b>"
    )


async def _react_description(state: FSMContext, query: CallbackQuery):
    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text="<b>💭 Введите новое описание предмета</b>"
    )


@router.callback_query()
async def handle(
        query: CallbackQuery,
        state: FSMContext):
    print(query.data)
