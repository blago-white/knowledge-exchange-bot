from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.callback.utils.data import (DepositMakingApprovationData,
                                          DepositPaymentApproveData)


def get_deposit_approvation_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❇ Пополняем",
                              callback_data=DepositMakingApprovationData(
                                  approve=True
                              ).pack()),
         InlineKeyboardButton(text="❌ Отменяем",
                              callback_data=DepositMakingApprovationData(
                                  approve=False
                              ).pack())]
    ])


def get_payment_approve_kb(admin_view: bool = False, deposit_id: int = -1):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Перевел",
            callback_data=DepositPaymentApproveData(
                admin_view=admin_view,
                to_admin_deposit_id=deposit_id
            ).pack()
        )]
    ])
