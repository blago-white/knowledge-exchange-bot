import re

from aiogram.types.message import Message
from aiogram.filters.callback_data import CallbackQuery
from functools import wraps

from services.base import BaseModelService


def _convert_class_name(class_name: str) -> str:
    return re.sub(
        r'(?<!^)(?=[A-Z])',
        '_',
        class_name.__name__
    ).lower()


def provide_model_service(*services: list[BaseModelService]):
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            print("WRAPPED")

            try:
                message: Message = kwargs.get(
                    "message", [a for a in args if a.__class__ is Message][0]
                )
            except IndexError:
                try:
                    query: CallbackQuery = kwargs.get(
                        "query", [a for a in args if a.__class__ is CallbackQuery][0]
                    )
                    message = query.message
                except IndexError:
                    raise Exception("Cannot get user!")

            return await func(
                *args, **(kwargs | {
                    _convert_class_name(class_name=r): r(
                        worker_id=message.chat.id
                    )
                    for r in services
                })
            )
        return wrapped
    return wrapper

