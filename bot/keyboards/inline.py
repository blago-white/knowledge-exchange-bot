from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.callback.utils.data import RenderProfileData, UpdateProfileInfoData, ProfileUpdateField


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
                callback_data=RenderProfileData(
                    show_profile=True
                ).pack()
            ), InlineKeyboardButton(
                text="📆 Расписание",
                callback_data=RenderProfileData(
                    show_profile=True
                ).pack()
            )]
        ]
    )


def get_profile_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="⬅ В меню",
                callback_data=RenderProfileData(
                    show_profile=False
                ).pack()
            )], [InlineKeyboardButton(
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
            )]
        ]
    )

