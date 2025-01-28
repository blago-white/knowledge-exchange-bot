from aiogram import Router
from aiogram.filters.command import CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.worker import WorkersService
from services.student import StudentsService, StudentInitializingData
from services.lesson import SubjectsService, SubjectsInitializingData

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
@provide_model_service(StudentsService, SubjectsService)
async def register_student(message: Message,
                           command: CommandObject,
                           state: FSMContext,
                           students_service: StudentsService,
                           subjects_service: SubjectsService):
    try:
        values = command.args.split(" ", 4)

        if len(values) != 5:
            raise ValueError("Incorrect length of arguments")
    except:
        return await message.reply(
            "ℹ Для создания ученика оптправьте - \n\n"
            "/add *Имя ученика* *Город ученика* *Ставка* "
            "*Название предмета через тире (Информатика-ЕГЭ)* "
            "*Описание*\n\n"
            "<i>/add Евгений Ростов-На-Дону 950 Русский-Олимпиада 8 класс, Уровень знаний - средний</i>"
        )

    try:
        student_data = StudentInitializingData(
            name=values[0],
            city=values[1],
            default_rate=int(values[2]),
            description=values[-1],
        )

        student_id = await students_service.initialize(
            student_data=student_data
        )
        try:
            await subjects_service.initialize(
                data=SubjectsInitializingData(
                    worker_id=message.chat.id,
                    student_id=student_id,
                    rate=int(values[2]),
                    title=values[3]
                )
            )
        except:
            await students_service.repository.drop_unauthorized(
                student_id=student_id
            )
            raise ValueError("Subject creation failed!")
    except Exception:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="❌Перепроверьте корректность данных еще разок..."
        )
    else:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="❇<b>Поздравляем, ученик добавлен! Удачных уроков!</b>\n\n"
                 f"А чтобы и ему(ей) было удобно, "
                 f"и чтобы вы смогли продать ученика,"
                 f"попросите перейти в этот бот по такой ссылке:"
                 f"\n"
                 f"<code>t.me/ZnanieExBot?start=student={student_id}</code>"
        )
