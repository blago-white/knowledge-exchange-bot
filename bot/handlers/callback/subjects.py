from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F

from services.lesson import Subject, SubjectsService
from handlers.callback.utils.data import StopSubjectData
from keyboards.inline import get_subject_details_kb

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


@router.callback_query(StopSubjectData.filter(F.subject_id != None))
@provide_model_service(SubjectsService)
async def subject_deactivate(
        query: CallbackQuery,
        callback_data: StopSubjectData,
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


@router.callback_query()
async def show_(
        query: CallbackQuery,
        state: FSMContext):
    print(query.data, "WQWW")
