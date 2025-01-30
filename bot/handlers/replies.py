START_MESSAGE = """
<b>⚜ Меню</b> [<code>{user_id}</code>] ⚜

✅ <i>Проданных учеников — <b>{selled_students}</b></i>
📈 <i>Заработок в неделю — <b>{week_profit}₽</b></i>
💰 <i>Всего забаротано — <b>{total_profit}₽</b></i>
🔗 <i>Рефералов приведено — <b>{referals_count}</b></i>

🌐 <b> Google meet: </b> <code>{meet_link}</code>
"""

ACCOUNT_DATA_MESSAGE = """
🙍‍♂️ Ваш профиль, <b>{first_name}</b>

☎ — <code>{phone_number}</code>
💳 — <code>{bank_card_number}</code>
🌐 — <code>{meet_link}</code>

— <i>{desctiption}</i>
"""

LESSON_DATA_MESSAGE = """
📚 <b>Урок {free_label} от {date} </b>
<i>⏳ {duration}</i>
<i>{status}</i>

<i>Запись — </i>{record_link}
"""

STUDENT_START_MESSAGE = """
<b>⚜ Здравствуйте, {student_name} ⚜</b>

💰 <i>Ваш баланс на занятия — <b>{balance}</b></i>
{next_lesson}
"""

STUDENT_NEXT_LESSON_LABEL_EXISTS = """
⏰ <i>Ближайший урок — <b>{next_lesson_date}</b></i>
📕 <i>Предмет — <b>{next_lesson_subject}</b></i>
⏳ <i>Длительность — <b>{next_lesson_duration}</b></i>
🌐 <b> Ссылка на занятие: </b> <code>{meet_link}</code>
"""

STUDENT_NEXT_LESSON_LABEL_EMPTY = """
⏰ <i>В ближайшее время уроков не запланировано, 
но <b>не забывайте развиваться)</b></i>
"""