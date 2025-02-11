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
    seller_view: int = False


class GetSubjectLessonsData(CallbackData, prefix="subject-lessons"):
    subject_id: int
    seller_view: bool
    only_show_legend: bool = False


class ShowLessonInfoData(CallbackData, prefix="lesson-info"):
    lesson_id: int
    seller_id: int = -1
    seller_view: bool = False


class ShowWeekSchedule(CallbackData, prefix="week-schedule"):
    week_number: int = 0
    beta: bool = False
    alpha: int = 49385394875


class AddLessonData(CallbackData, prefix="lesson-add"):
    subject_id: int = 0


class LessonCommitViewCallbackData(CallbackData, prefix="lesson-commit"):
    make_free: bool = False
    make_scheduled: bool = False
    commit_lesson: bool = False


class DropLessonData(CallbackData, prefix="lesson-drop"):
    many: bool = False
    lesson_id: int = -1


class MakeWithdrawData(CallbackData, prefix="make-withdraw"):
    pass


class SelledStudentsList(CallbackData, prefix="selled-list"):
    pass


class SellStudentData(CallbackData, prefix="sell-student"):
    subject_id: int


class SellApprovationData(CallbackData, prefix="sell-approve"):
    approve: bool


class SellOfferAcceptingData(CallbackData, prefix="sell-accept"):
    accept: bool
    offer_id: int


class MyChatsListData(CallbackData, prefix="chats"):
    pass


class LessonCompliteData(CallbackData, prefix="complete-lesson"):
    lesson_id: int
