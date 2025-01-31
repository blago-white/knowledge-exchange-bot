import typing
from enum import Enum

from aiogram.filters.callback_data import CallbackData


class ProfileUpdateField(Enum):
    PHONE = "P"
    CARD = "C"
    LINK = "L"
    DESCRIPTION = "D"


class WorkerSubjectsFilters(Enum):
    ALL = "A"


TO_HOME_DATA = "go-to-profile"


class RenderProfileData(CallbackData, prefix="profile"):
    show_profile: bool


class UpdateProfileInfoData(CallbackData, prefix="profile-update"):
    update_field: ProfileUpdateField


class GetWorkerSubjectsData(CallbackData, prefix="subjects-all"):
    filter: WorkerSubjectsFilters


class StudentProfileData(CallbackData, prefix="student"):
    subject_id: int


class GetSubjectLessonsData(CallbackData, prefix="subject-lessons"):
    subject_id: int
    only_show_legend: bool = False


class ShowLessonInfoData(CallbackData, prefix="lesson-info"):
    lesson_id: int


class ShowWeekSchedule(CallbackData, prefix="week-schedule"):
    week_number: int = 0


class AddLessonData(CallbackData, prefix="lesson-add"):
    subject_id: int = 0


class LessonCommitViewCallbackData(CallbackData, prefix="lesson-commit"):
    make_free: bool = False
    make_scheduled: bool = False
    commit_lesson: bool = False


class DropLessonData(CallbackData, prefix="lesson-drop"):
    many: bool = False
    lesson_id: int = None
