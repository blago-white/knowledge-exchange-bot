from aiogram import Router
from aiogram.filters.command import CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.worker import WorkersService
from ..providers import provide_model_service
from ..states.profile import UpdateProfileData

router = Router(name=__name__)

_UPDATE_FIELD_NAME_BY_STATE = {
    UpdateProfileData.update_card: "bank_card_number",
    UpdateProfileData.update_phone: "phone_number",
    UpdateProfileData.update_link: "meet_link",
    UpdateProfileData.update_description: "description"
}


@router.message(UpdateProfileData())
@provide_model_service(WorkersService)
async def update_profile_info(
        message: Message,
        state: FSMContext,
        workers_service: WorkersService):
    state_obj: UpdateProfileData = await state.get_state()

    try:
        result = await workers_service.repository.update(
            pk=message.chat.id,
            **{_UPDATE_FIELD_NAME_BY_STATE[state_obj]: message.text}
        )
    except Exception as e:
        await message.reply(text=f"❌ {str(e)}")
        await message.reply(text=f"Попробуйте ввести еще раз, "
                                 f"либо отправьте /start")
        return
    else:
        print(result.phone_number)

        await message.reply(text="✅Запомнили!")
        await state.clear()


@router.message(Command("add"))
async def register_student(message: Message,
                           command: CommandObject,
                           state: FSMContext):
    if not command.args:
        return await message.reply(
            "ℹ Для создания ученика оптправьте - \n\n"
            "/add *Имя ученика* *Город ученика* *Ставка* "
            "*Название предмета через тире (Информатика-ЕГЭ)* "
            "*Описание (опционально)*\n\n"
            "<i>/add Евгений Ростов-На-Дону 950 Русский-Олимпиада 8 класс, Уровень знаний - средний</i>"
        )

    print(command.args.split(" ", 4))
