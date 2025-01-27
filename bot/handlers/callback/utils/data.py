from enum import Enum

from aiogram.filters.callback_data import CallbackData


class ProfileUpdateField(Enum):
    PHONE = "P"
    CARD = "C"
    LINK = "L"
    DESCRIPTION = "D"


class RenderProfileData(CallbackData, prefix="profile"):
    show_profile: bool


class UpdateProfileInfoData(CallbackData, prefix="profile-update"):
    update_field: ProfileUpdateField
