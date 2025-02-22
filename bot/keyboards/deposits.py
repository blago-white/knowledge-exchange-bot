from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.callback.utils.data import DepositMakingApprovationData


def get_deposit_approvation_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❇ Пополняем",
                              callback_data=DepositMakingApprovationData(
                                  approve=True
                              )),
         InlineKeyboardButton(text="❌ Отменяем",
                              callback_data=DepositMakingApprovationData(
                                  approve=False
                              ))]
    ])
