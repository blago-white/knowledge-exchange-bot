import datetime

import pytz

from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.callback.utils.data import (TO_HOME_DATA,
                                          RenderProfileData,
                                          UpdateProfileInfoData,
                                          ProfileUpdateField,
                                          GetWorkerSubjectsData,
                                          WorkerSubjectsFilters,
                                          StudentProfileData,
                                          GetSubjectLessonsData)

from models.lesson import Lesson, Subject, LessonStatus


def get_home_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🙍‍♂️ Мой Профиль",
                callback_data=RenderProfileData(
                    show_profile=True
                ).pack()
            ), InlineKeyboardButton(
                text="📕 Мои Ученики",
                callback_data=GetWorkerSubjectsData(
                    filter=WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="📆 Расписание",
                callback_data="None"
            )]
        ]
    )


def get_profile_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="☎ Указать телефон",
                callback_data=UpdateProfileInfoData(
                    update_field=ProfileUpdateField.PHONE
                ).pack()
            ), InlineKeyboardButton(
                text="💳 Указать карту выплат",
                callback_data=UpdateProfileInfoData(
                    update_field=ProfileUpdateField.CARD
                ).pack()
            )], [InlineKeyboardButton(
                text="🌐 Указать ссылку звонка",
                callback_data=UpdateProfileInfoData(
                    update_field=ProfileUpdateField.LINK
                ).pack()
            ), InlineKeyboardButton(
                text="💪 Пару слов о вас",
                callback_data=UpdateProfileInfoData(
                    update_field=ProfileUpdateField.DESCRIPTION
                ).pack()
            )],
            [InlineKeyboardButton(
                text="⬅ В меню",
                callback_data=TO_HOME_DATA
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
                callback_data=StudentProfileData(
                    subject_id=subject.id
                ).pack()
            )] for subject, till_text in zip(subjects, subjects_table)],
            [InlineKeyboardButton(
                text="⬅ В меню",
                callback_data=TO_HOME_DATA
            )]
        ]
    )


def get_subject_details_kb(subject: Subject):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📆 Тут уроки",
                callback_data=GetSubjectLessonsData(
                    subject_id=subject.id
                ).pack()
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
                callback_data=GetWorkerSubjectsData(
                    filter=WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=TO_HOME_DATA
            )],
        ]
    )


def get_subject_lessons_kb(subject_id: int, lessons: list[Lesson]):
    # ✅ 10.01 12:30 0.5ч
    # ❌ 10.01 18:550.5ч
    # ☑ 10.01 20:10 0.5ч

    lessons_kb, lessons_kb_row = [], []
    lesson_datetime_format = "%m.%d %H:%M"

    LESSON_STATUSES = {
        LessonStatus.SUCCESS: "✅",
        LessonStatus.CANCELED: "❌",
        LessonStatus.SCHEDULED: "☑"
    }

    for lesson in lessons:
        lesson_date_utc: datetime.datetime = lesson.date
        lesson_date_msc = lesson_date_utc.astimezone(pytz.timezone("Europe/Moscow"))

        lesson_status = LESSON_STATUSES[lesson.status]

        if lesson.status == LessonStatus.SCHEDULED and datetime.datetime.now(tz=pytz.UTC) > lesson_date_utc:
            lesson_status = "⁉"

        lessons_kb_row.append(InlineKeyboardButton(
            text=f"{lesson_status} "
                 f"{lesson_date_msc.strftime(lesson_datetime_format)} МСК "
                 f"{lesson.duration/60}ч",
            callback_data="None"
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
                text="👤⬅ Обратно",
                callback_data=StudentProfileData(
                    subject_id=subject_id
                ).pack()
            )],
            [InlineKeyboardButton(
                text="📕⬅ К списку учеников",
                callback_data=GetWorkerSubjectsData(
                    filter=WorkerSubjectsFilters.ALL
                ).pack()
            ), InlineKeyboardButton(
                text="⬅ К меню",
                callback_data=TO_HOME_DATA
            )],
        ]
    )
