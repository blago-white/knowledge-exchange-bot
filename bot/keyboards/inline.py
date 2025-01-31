import copy
import datetime
import pytz

from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.callback.utils import data
from models.lesson import Lesson, Subject, LessonStatus

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
                callback_data=data.GetWorkerSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="📆 Расписание",
                callback_data=data.ShowWeekSchedule().pack()
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
                    subject_id=subject.id
                ).pack()
            )] for subject, till_text in zip(subjects, subjects_table)],
            [InlineKeyboardButton(
                text="⬅ В меню",
                callback_data=data.TO_HOME_DATA
            )]
        ]
    )


def get_subject_details_kb(subject: Subject):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📆 Тут уроки",
                callback_data=data.GetSubjectLessonsData(
                    subject_id=subject.id
                ).pack()
            )],
            [InlineKeyboardButton(
                text="➕ Новый урок (-и)",
                callback_data=data.AddLessonData(subject_id=subject.id).pack()
            )],
            [InlineKeyboardButton(
                text="🏁 Уже закончили учится"
                if subject.is_active else
                "🏳 Вернуть активный статус",
                callback_data="None"
            )],
            [InlineKeyboardButton(
                text="✏ Кое-что нужно поправить",
                callback_data="None"
            )],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=data.GetWorkerSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=data.TO_HOME_DATA
            )],
        ]
    )


def get_subject_lessons_kb(subject_id: int, lessons: list[Lesson]):
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
                lesson_id=lesson.id
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
                    subject_id=subject_id
                ).pack()
            ), InlineKeyboardButton(
                text="❓Что это обозначает?",
                callback_data=data.GetSubjectLessonsData(
                    subject_id=subject_id,
                    only_show_legend=True
                ).pack()
            )],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=data.GetWorkerSubjectsData(
                    filter=data.WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=data.TO_HOME_DATA
            )],
        ]
    )


def get_lesson_data_inline_kb(subject_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="👥 Учитель",
                callback_data="None"
            )],
            [InlineKeyboardButton(
                text="👤⬅ К ученику",
                callback_data=data.StudentProfileData(
                    subject_id=subject_id
                ).pack()
            )],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=data.GetWorkerSubjectsData(
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

    current_day = convert_date_to_day(lessons[0].display_date)

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
            text=f"⚜ {get_day_label(date=lessons[0].date_msc)} "
                 f"{convert_date_to_day(lessons[0].display_date)} ⚜",
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
                text=f"⚜ {get_day_label(date=lesson.date_msc)} {lesson_date} ⚜",
                callback_data="None"
            )])

            day_lessons_buttons.clear()
            day_lessons_buttons_pair.clear()

            current_day = lesson_date

        day_lessons_buttons_pair.append(InlineKeyboardButton(
            text=f"{lesson_status} "
                 f"{lesson.display_date} "
                 f"{lesson.display_duration}",
            callback_data=data.ShowLessonInfoData(
                lesson_id=lesson.id
            ).pack()
        ))

        if len(day_lessons_buttons_pair) == 2 or current_day != lesson_date:
            day_lessons_buttons.append(day_lessons_buttons_pair.copy())
            day_lessons_buttons_pair.clear()
    else:
        if len(day_lessons_buttons_pair) == 1:
            lessons_kb.append([day_lessons_buttons_pair.pop()])

    lessons_kb.append([
        InlineKeyboardButton(
            text="⬅ К меню",
            callback_data=data.TO_HOME_DATA
        ),
        InlineKeyboardButton(
            text="❎ Как закончите - нажмите" if lessons_dropping_mode else "⛔ Удалить урок (-и)",
            callback_data=data.DropLessonData().pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=lessons_kb)


def get_lesson_commiting_kb(is_free: bool = False, is_scheduled: bool = False):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="☑ Бесплатный урок" if not is_free else "✅ Бесплатный урок",
                callback_data=data.LessonCommitViewCallbackData(
                    make_free=True
                ).pack()
            )],
            [InlineKeyboardButton(
                text="🕒 Сделать постоянным"
                if not is_scheduled else
                "🕒 Уже постоянный",
                callback_data=data.LessonCommitViewCallbackData(
                    make_scheduled=True
                ).pack()
            )],
            [InlineKeyboardButton(
                text="📌 Создать урок",
                callback_data=data.LessonCommitViewCallbackData(
                    commit_lesson=True
                ).pack()
            )],
        ]
    )
