from aiogram import Router, F
from aiogram.types.input_file import InputFile, FSInputFile
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.fsm.context import FSMContext

from .utils.data import ABOUT_INFO_DATA

router = Router(name=__name__)


@router.callback_query(F.data == ABOUT_INFO_DATA)
async def show_about(query: CallbackQuery):
    await query.message.bot.send_photo(
        chat_id=query.message.chat.id,
        caption="""<span class="tg-spoiler">Я - Богдан, фулл-стек разработчик на Python с опытом 5 лет\n
В прошлом работал репетитором 2 года, успел поработать в Luxkode, 
но основную часть времени я работал <b>на себя</b>,
это и побудило меня создать универсальную утилиту для оптимизации работы.</span>

Этот бот существует исключительно из - за этого —

<i>1️⃣ Легче получить ученика по 1 клику, чем искать его самому</i>

<i>2️⃣ Легче продать ученика по 1 клику, чем договариваться с покупателем</i>

<i>3️⃣ Легче передать всю работу <b><i>Знания.Про</i></b>, чем самому решать проблемы с коммуникациями</i>

<i>4️⃣ Легче видеть четкую метрику перед глазами, чем расчитывать ее в калькуляторе</i>

<i>5️⃣ Спокойнее когда за сделку отвечает "машина" а не серые персоны</i>

<i>ИНН - <code>312348585325</code></i>
<i>ОГРНИП - <code>323310000063180</code></i>
<i>2025 ИП Логинов Богдан Николаевич, все права на бот и его содержание защищены, 
любое несанкционирование использование контента из бота запрещено!</i>
""",
        photo=FSInputFile(
            "D:\FDISKCOPY\python\knowledge-exchange-bot\\bot\static\iam.jpg"
        ),
    )
