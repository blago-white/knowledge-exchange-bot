import copy
import datetime
import pytz

from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.callback.utils import data
from models.lesson import Lesson, Subject, LessonStatus
from models.dialog import Message
from models.student import StudentSellOffer

_LESSON_STATUSES = {
    LessonStatus.SUCCESS: "✅",
    LessonStatus.CANCELED: "❌",
    LessonStatus.SCHEDULED: "🔔"
}


def get_home_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🙍‍♂️ Мой Профиль",
                callback_data=data.RenderProfileData(
                    show_profile=True
                ).pack()
            ), InlineKeyboardButton(
                text="📕 Мои Ученики",
                callback_data=data.GetSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="📆 Расписание",
                callback_data=data.ShowWeekSchedule().pack()
            )],
            [InlineKeyboardButton(
                text="💸 Вывести",
                callback_data=data.MakeWithdrawData().pack()
            ), InlineKeyboardButton(
                text="🗃 Проданные Ученики",
                callback_data=data.SelledStudentsList().pack()
            ), InlineKeyboardButton(
                text="💬 Ваши Чаты",
                callback_data=data.MyChatsListData().pack()
            )],
            [InlineKeyboardButton(
                text="🛡 О \"ИП Логинов Богдан Николаевич\"",
                callback_data=data.ABOUT_INFO_DATA
            )]
        ]
    )


def get_profile_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="☎ Указать телефон",
                callback_data=data.UpdateProfileInfoData(
                    update_field=data.ProfileUpdateField.PHONE
                ).pack()
            ), InlineKeyboardButton(
                text="💳 Указать карту выплат",
                callback_data=data.UpdateProfileInfoData(
                    update_field=data.ProfileUpdateField.CARD
                ).pack()
            )], [InlineKeyboardButton(
                text="🌐 Указать ссылку звонка",
                callback_data=data.UpdateProfileInfoData(
                    update_field=data.ProfileUpdateField.LINK
                ).pack()
            ), InlineKeyboardButton(
                text="💪 Пару слов о вас",
                callback_data=data.UpdateProfileInfoData(
                    update_field=data.ProfileUpdateField.DESCRIPTION
                ).pack()
            )],
            [InlineKeyboardButton(
                text="⬅ В меню",
                callback_data=data.TO_HOME_DATA
            )]
        ]
    )


def get_subjects_table_kb(subjects: list[Subject]):
    subjects_table = [
        (f"📍#{s.id} {s.student.name}, {s.student.city} | "
         f"{s.title} | {s.rate}₽")
        for s in subjects
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *[[InlineKeyboardButton(
                text=till_text,
                callback_data=data.StudentProfileData(
                    subject_id=subject.id,
                    seller_view=False
                ).pack()
            )] for subject, till_text in zip(subjects, subjects_table)],
            [InlineKeyboardButton(
                text="⬅ В меню",
                callback_data=data.TO_HOME_DATA
            )]
        ]
    )


def get_subject_details_kb(
        subject: Subject,
        seller_view: bool = True,
        seller_id: int = None):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📆 Тут уроки",
                callback_data=data.GetSubjectLessonsData(
                    subject_id=subject.id,
                    seller_view=seller_view,
                    seller_id=seller_id
                ).pack()
            )],
            [InlineKeyboardButton(
                text="➕ Новый урок (-и)",
                callback_data=data.AddLessonData(subject_id=subject.id).pack()
            )] if not seller_view else [],
            [InlineKeyboardButton(
                text="🏁 Уже закончили учится"
                if subject.is_active else
                "🏳 Вернуть активный статус",
                callback_data=data.StopSubjectData(
                    subject_id=subject.id).pack()
            )] if not seller_view else [],
            [InlineKeyboardButton(
                text="✏ Кое-что нужно поправить",
                callback_data=data.EditSubjectData(
                    open_menu=True,
                    subject_id=subject.id,
                ).pack()
            )] if not seller_view else [],
            [InlineKeyboardButton(
                text="💰 Продать ученика",
                callback_data=data.SellStudentData(
                    subject_id=subject.id
                ).pack()
            )] if not seller_view else [],
            [InlineKeyboardButton(
                text="💬 Написать сообщение" if subject.student.telegram_id is not None else "❌💬 Ученик не перешел по ссылке",
                callback_data=data.SendMessageData(
                    subject_id=subject.id,
                    recipient_id=subject.student.telegram_id or 0
                ).pack()
            )],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=data.GetSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=data.TO_HOME_DATA
            )],
        ]
    )


def get_subject_edit_kb(subject_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🔖 Изменить название",
                callback_data=data.EditSubjectData(
                    open_menu=False,
                    subject_id=subject_id,
                    edit_field=data.SubjectEditField.TITLE
                ).pack()
            ), InlineKeyboardButton(
                text="💭 Изменить описание",
                callback_data=data.EditSubjectData(
                    open_menu=False,
                    subject_id=subject_id,
                    edit_field=data.SubjectEditField.DESCRIPTION
                ).pack()
            ), InlineKeyboardButton(
                text="🕑 Изменить ставку",
                callback_data=data.EditSubjectData(
                    open_menu=False,
                    subject_id=subject_id,
                    edit_field=data.SubjectEditField.RATE
                ).pack()
            )],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=data.GetSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=data.TO_HOME_DATA
            )],
        ]
    )


def get_subject_lessons_kb(
        subject_id: int,
        lessons: list[Lesson],
        seller_id: int = -1,
        seller_view: bool = False):
    lessons_kb, lessons_kb_row = [], []

    for lesson in lessons:
        lesson_status = _LESSON_STATUSES[lesson.status]

        if lesson.status == LessonStatus.SCHEDULED and datetime.datetime.now(
                tz=pytz.UTC) > lesson.date:
            lesson_status = "⁉"

        lessons_kb_row.append(InlineKeyboardButton(
            text=f"{lesson_status} "
                 f"{lesson.display_date} "
                 f"{lesson.display_duration}",
            callback_data=data.ShowLessonInfoData(
                lesson_id=lesson.id,
                seller_view=seller_view,
                seller_id=seller_id,
            ).pack()
        ))

        if len(lessons_kb_row) == 3:
            lessons_kb.append(lessons_kb_row.copy())
            lessons_kb_row.clear()
    else:
        lessons_kb.append(lessons_kb_row)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *lessons_kb,
            [InlineKeyboardButton(
                text="👤⬅ К ученику",
                callback_data=data.StudentProfileData(
                    subject_id=subject_id,
                    seller_view=False
                ).pack()
            ), InlineKeyboardButton(
                text="❓Что это обозначает?",
                callback_data=data.GetSubjectLessonsData(
                    subject_id=subject_id,
                    only_show_legend=True,
                    seller_view=seller_view
                ).pack()
            )],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=data.GetSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=data.TO_HOME_DATA
            )],
        ]
    )


def get_lesson_data_inline_kb(
        lesson_id: int, subject_id: int, seller_view: bool = False):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="👥 Учитель",
                callback_data="None"
            )],
            [InlineKeyboardButton(
                text="⛔ Удалить урок",
                callback_data=data.DropLessonData(
                    lesson_id=lesson_id,
                    many=False
                ).pack()
            ), InlineKeyboardButton(
                text="✅ Провели урок",
                callback_data=data.LessonCompliteData(
                    lesson_id=lesson_id
                ).pack()
            ), InlineKeyboardButton(
                text="✏ Изменить",
                callback_data=data.EditLessonData(open_menu=True,
                                                  lesson_id=lesson_id,
                                                  subject_id=subject_id).pack()
            )] if not seller_view else [],
            [InlineKeyboardButton(
                text="👤⬅ К ученику",
                callback_data=data.StudentProfileData(
                    subject_id=subject_id,
                    seller_view=False
                ).pack()
            ), InlineKeyboardButton(
                text="📆⬅ К урокам",
                callback_data=data.GetSubjectLessonsData(
                    subject_id=subject_id,
                    seller_view=False
                ).pack()
            )] if not seller_view else [],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=data.GetSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=data.TO_HOME_DATA
            )],
        ]
    )


def get_week_schedule_keyboard(
        lessons: list[Lesson],
        lessons_dropping_mode: bool = False):
    lessons_kb, day_lessons_buttons, day_lessons_buttons_pair = [], [], []
    convert_date_to_day = lambda date: date.split(" ")[0].replace(" ", "")
    controls = [
        InlineKeyboardButton(
            text="⬅ К меню",
            callback_data=data.TO_HOME_DATA
        ),
        InlineKeyboardButton(
            text="❎ Как закончите - нажмите" if lessons_dropping_mode else "⛔ Удалить урок (-и)",
            callback_data=data.DropLessonData(lesson_id=1,
                                              many=True).pack()
        )
    ]

    try:
        current_day = convert_date_to_day(lessons[0].display_date)
    except:
        return InlineKeyboardMarkup(inline_keyboard=[controls])

    def get_day_label(date: datetime.datetime):
        return ["Понедельник",
                "Вторник",
                "Среда",
                "Четверг",
                "Пятница",
                "Суббота",
                "Воскресенье"][date.weekday()]

    if lessons:
        lessons_kb.append([InlineKeyboardButton(
            text=f"{get_day_label(date=lessons[0].date_msc)} "
                 f"{convert_date_to_day(lessons[0].display_date)}",
            callback_data="None"
        )])

    for lesson in lessons:
        lesson_status = _LESSON_STATUSES[lesson.status]

        if lesson.status == LessonStatus.SCHEDULED and datetime.datetime.now(
                tz=pytz.UTC) > lesson.date:
            lesson_status = "⁉"

        lesson_date = convert_date_to_day(lesson.display_date)

        if current_day != lesson_date:
            lessons_kb.extend(copy.deepcopy(day_lessons_buttons))

            if len(day_lessons_buttons_pair) == 1:
                lessons_kb.append([day_lessons_buttons_pair.pop()])

            lessons_kb.append([InlineKeyboardButton(
                text=f"{get_day_label(date=lesson.date_msc)} {lesson_date}",
                callback_data="None"
            )])

            day_lessons_buttons.clear()
            day_lessons_buttons_pair.clear()

            current_day = lesson_date

        day_lessons_buttons_pair.append(InlineKeyboardButton(
            text=f"{"🎁" if lesson.is_free else ""}{lesson_status} "
                 f"{lesson.subject.title} | "
                 f"{lesson.display_duration}",
            callback_data=data.ShowLessonInfoData(
                lesson_id=lesson.id,
                seller_view=False
            ).pack()
        ))

        if len(day_lessons_buttons_pair) == 2 or current_day != lesson_date:
            day_lessons_buttons.append(day_lessons_buttons_pair.copy())
            day_lessons_buttons_pair.clear()
    else:
        if len(day_lessons_buttons_pair) == 1:
            lessons_kb.append([day_lessons_buttons_pair.pop()])

    lessons_kb.append(controls)

    return InlineKeyboardMarkup(inline_keyboard=lessons_kb)


def get_lesson_commiting_kb(is_free: bool = False, schedule: int = None):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{"🕒" if schedule != 2 else "✅"} x2",
                callback_data=data.LessonCommitViewCallbackData(
                    make_free=True,
                    make_scheduled=True,
                    schedule_factor=2,
                ).pack()
            ), InlineKeyboardButton(
                text=f"{"🕒" if schedule != 3 else "✅"} x3",
                callback_data=data.LessonCommitViewCallbackData(
                    make_free=True,
                    make_scheduled=True,
                    schedule_factor=3,
                ).pack()
            ), InlineKeyboardButton(
                text=f"{"🕒" if schedule != 4 else "✅"} x4",
                callback_data=data.LessonCommitViewCallbackData(
                    make_free=True,
                    make_scheduled=True,
                    schedule_factor=4,
                ).pack()
            )],
            [InlineKeyboardButton(
                text="☑ Бесплатный урок" if not is_free else "✅ Бесплатный урок",
                callback_data=data.LessonCommitViewCallbackData(
                    make_free=True
                ).pack()
            )],
            # [InlineKeyboardButton(
            #     text="🕒 Сделать постоянным"
            #     if not is_scheduled else
            #     "🕒 Уже постоянный",
            #     callback_data=data.LessonCommitViewCallbackData(
            #         make_scheduled=True
            #     ).pack()
            # )],
            [InlineKeyboardButton(
                text="📌 Создать урок",
                callback_data=data.LessonCommitViewCallbackData(
                    commit_lesson=True
                ).pack()
            )],
        ]
    )


def get_selled_list_inline_kb(selled: list[StudentSellOffer]):
    selled_kb = []

    for s in selled:
        selled_kb.append([InlineKeyboardButton(
            text=f"{"✅" if s.is_paid else (
                "✴" if s.is_accepted else "📤"
            )} | "
                 f"{s.subject.student.name} | "
                 f"{s.subject.title} | "
                 f"{s.paid_sum}₽/{s.cost}₽",
            callback_data=data.StudentProfileData(
                subject_id=s.subject.id,
                seller_view=True
            ).pack()
        )])

    selled_kb.append([InlineKeyboardButton(
        text="⬅ К меню",
        callback_data=data.TO_HOME_DATA
    )])

    return InlineKeyboardMarkup(inline_keyboard=selled_kb)


def get_sell_approve_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Все так!",
                callback_data=data.SellApprovationData(
                    approve=True
                ).pack()
            ), InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=data.SellApprovationData(
                    approve=False
                ).pack()
            )]
        ]
    )


def get_accept_sell_offer_kb(offer_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ Принять",
                callback_data=data.SellOfferAcceptingData(
                    accept=True,
                    offer_id=offer_id
                ).pack()
            ), InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=data.SellOfferAcceptingData(
                    accept=False,
                    offer_id=offer_id
                ).pack()
            )
        ]]
    )


def get_edit_lesson_kb(lesson_id: int, subject_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="👥 Учитель",
                callback_data="None"
            )],
            [InlineKeyboardButton(
                text="⛔ Удалить урок",
                callback_data=data.DropLessonData(
                    lesson_id=lesson_id,
                    many=False
                ).pack()
            ), InlineKeyboardButton(
                text="✅ Провели урок",
                callback_data=data.LessonCompliteData(
                    lesson_id=lesson_id
                ).pack()
            )],
            [InlineKeyboardButton(
                text="🎥 Изменить запись",
                callback_data=data.EditLessonData(
                    open_menu=False,
                    lesson_id=lesson_id,
                    subject_id=subject_id,
                    edit_date=False,
                    edit_record_link=True
                ).pack()
            ), InlineKeyboardButton(
                text="📆 Изменить дату и длительность",
                callback_data=data.EditLessonData(
                    open_menu=False,
                    lesson_id=lesson_id,
                    subject_id=subject_id,
                    edit_record_link=False,
                    edit_date=True
                ).pack()
            )],
            [InlineKeyboardButton(
                text="👤⬅ К ученику",
                callback_data=data.StudentProfileData(
                    subject_id=subject_id,
                    seller_view=False
                ).pack()
            ), InlineKeyboardButton(
                text="📆⬅ К урокам",
                callback_data=data.GetSubjectLessonsData(
                    subject_id=subject_id,
                    seller_view=False
                ).pack()
            )],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=data.GetSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=data.TO_HOME_DATA
            )],
        ]
    )


def get_chats_keyboard(previews: list[Message]):
    chats_kb = []

    for p in previews:
        chats_kb.append([InlineKeyboardButton(
            text=f"{p.subject.student.name} | {p.subject.student.city} [{p.subject.title}]",
            callback_data=data.OpenChatData(subject_id=p.subject_id).pack()
        )])

    chats_kb.append([InlineKeyboardButton(
        text="⬅ К меню",
        callback_data=data.TO_HOME_DATA
    )])

    return InlineKeyboardMarkup(inline_keyboard=chats_kb)


def get_student_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="➕ Пополнить баланс",
            callback_data=data.MakeDepositData().pack()
        )],
        [InlineKeyboardButton(
            text="📕 Мои предметы",
            callback_data=data.GetSubjectsData(
                filter=data.WorkerSubjectsFilters.ALL,
                worker_view=False
            ).pack()
        ), InlineKeyboardButton(
            text="📆 Расписание",
            callback_data=data.ShowWeekSchedule(worker_view=False).pack()
        ), InlineKeyboardButton(
            text="💬 Ваши Чаты",
            callback_data=data.MyChatsListData().pack()
        )]
    ])


def get_chat_message_reply_kb(subject_id: int,
                              parent_msg_id: int,
                              recipient_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📝 Ответить",
            callback_data=data.SendMessageData(
                subject_id=subject_id,
                parent_msg_id=parent_msg_id,
                recipient_id=recipient_id
            ).pack()
        )],
    ])
