from aiogram.filters.callback_data import CallbackData


class RenderProfileData(CallbackData, prefix="profile"):
    show_profile: bool
