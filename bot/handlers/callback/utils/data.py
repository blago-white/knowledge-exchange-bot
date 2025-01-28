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
