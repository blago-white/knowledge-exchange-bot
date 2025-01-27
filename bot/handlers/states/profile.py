from aiogram.fsm.state import StatesGroup, State

from ..callback.utils.data import UpdateProfileInfoData, ProfileUpdateField


class UpdateProfileData(StatesGroup):
    update_phone = State()
    update_link = State()
    update_card = State()
    update_description = State()

    @classmethod
    def from_callback_data(
            cls, callback_data: UpdateProfileInfoData
    ) -> State:
        return {
            ProfileUpdateField.LINK: cls.update_link,
            ProfileUpdateField.PHONE: cls.update_phone,
            ProfileUpdateField.CARD: cls.update_card,
            ProfileUpdateField.DESCRIPTION: cls.update_description
        }.get(callback_data.update_field)
