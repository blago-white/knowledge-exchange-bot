from models.worker import Worker
from models.lesson import Lesson, LessonStatus, Subject
from models.student import Student, StudentSellOffer
from services.user import UserType
from models.dialog import Message
from services.worker import WorkersService


async def generate_main_stats_message_text(
        template: str,
        worker: Worker,
        workers_service: WorkersService
) -> str:
    week_profit = await workers_service.get_week_profit()

    return template.format(
        user_id=worker.id,
        balance=worker.balance,
        selled_students=await workers_service.get_selled_count(),
        week_profit=str(week_profit),
        total_profit=await workers_service.get_total_profit(),
        referals_count="Скоро будет...",
        meet_link=worker.meet_link or "А по этой ссылке ученики зайдут на урок!"
    )


def generate_lesson_data_message_text(
        template: str,
        lesson: Lesson
):
    lesson_status = {
        LessonStatus.SCHEDULED: "☑ Был запланирован",
        LessonStatus.SUCCESS: "✅ Проведен",
        LessonStatus.CANCELED: "❌ Отменен",
    }[lesson.status]

    free_label = None if not lesson.is_free else "<i>бесплатный</i>"

    return template.format(
        status=lesson_status,
        free_label=free_label or "",
        date=lesson.display_date,
        duration=lesson.display_duration,
        record_link=lesson.record_link or "<i>Упс... Запись не прекреплена</i>"
    )


def generate_student_main_message(template: str,
                                  next_lesson_template: str,
                                  next_lesson: Lesson,
                                  student: Student,
                                  meet_link: str = None):
    if next_lesson:
        next_lesson_template = next_lesson_template.format(
            next_lesson_date=next_lesson.display_date,
            next_lesson_subject=next_lesson.subject.title,
            next_lesson_duration=next_lesson.display_duration,
            meet_link=meet_link or "<i>Ссылки на звонок нет...Свяжитесь с преподавателем</i>"
        )

    return template.format(
        student_name=student.name,
        balance=int(student.balance),
        next_lesson=next_lesson_template
    )


def generate_subject_details_message(subject: Subject,
                                     selled_prefix: str = "") -> str:
    return f"""📍 {selled_prefix} <b>{subject.student.name} [{subject.student.city}]</b>
📕 Предмет — <i>{subject.title}
🕑 Ставка — {subject.rate}₽/ч</i>
👤 О ученике — <i>{subject.student.description or 'пока ничего не известно('}</i>

<i>{"— " + (subject.description or "Кажется, заметок еще нет!")}</i>
"""


def generate_dialog_history_message(self_type: UserType, dialog: list[Message]):
    text = f""

    for message in dialog:
        self_message = str(message.sender) == str(self_type)

        print(str(message.sender), str(self_type))

        text += (f"{"—" if self_message else "🗣 —"} "
                 f"[{message.display_sended_at}] "
                 f"<i>{message.text}</i>\n")

    return text
