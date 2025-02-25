from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.callback.utils.data import WithdrawSendedData


def get_withdraw_kb(worker_id: int, amount: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Вывод оформлен",
            callback_data=WithdrawSendedData(
                worker_id=worker_id,
                amount=amount
            ).pack()
        )]
    ])
