from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.callback.utils.data import SubjectEditField
from handlers.states.subjects import EditSubjectForm
from handlers.common.validators import subject as subject_validators
from services.lesson import SubjectsService
from handlers.common.utils.messages import generate_subject_details_message
from keyboards.inline import get_subject_details_kb

from ..providers import provide_model_service


router = Router(name=__name__)


@router.message(EditSubjectForm.edit_field)
@provide_model_service(SubjectsService)
async def edit_subject(
        message: Message,
        state: FSMContext,
        subjects_service: SubjectsService):
    field: SubjectEditField = (await state.get_data())["field"]

    try:
        validated_value = {
            SubjectEditField.TITLE: subject_validators.edit_subject_title,
            SubjectEditField.RATE: subject_validators.edit_subject_rate,
            SubjectEditField.DESCRIPTION: subject_validators.edit_subject_description}[
            field
        ](message.text)
    except ValueError as e:
        return await message.reply(f"❌ {str(e)}")
    except:
        return await message.reply("❌ Что-то пошло не так")

    value_name = {
        SubjectEditField.TITLE: "title",
        SubjectEditField.RATE: "rate",
        SubjectEditField.DESCRIPTION: "description"
    }[field]

    try:
        subject = await subjects_service.repository.update(
            pk=(await state.get_data())["subject_id"],
            **{value_name: validated_value}
        )
    except Exception as e:
        print(e)
        return await message.reply("❌ Не получилось сохранить, "
                                   "попробуйте позже или напишите в тп")

    await message.reply("✅ <b>Изменили</b>")

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=generate_subject_details_message(
            subject=subject,
        ),
        reply_markup=get_subject_details_kb(
            subject=subject,
            seller_view=False
        )
    )
