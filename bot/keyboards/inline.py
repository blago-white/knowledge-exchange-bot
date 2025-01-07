from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.callback.utils.data import RenderProfileData


def get_home_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🙍‍♂️ Мой Профиль",
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
            )]
        ]
    )

