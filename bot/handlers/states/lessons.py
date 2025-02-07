from aiogram.fsm.state import StatesGroup, State


class LessonCreationForm(StatesGroup):
    add_datetime = State()
    add_duration = State()


class DropLessonsForm(StatesGroup):
    drop_lesson = State()


class EditLessonDataForm(StatesGroup):
    edit_record_link = State()
    edit_datetime = State()
