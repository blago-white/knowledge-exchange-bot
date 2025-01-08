import re

from functools import wraps

from repositories.base import BaseModelRepository


def _convert_repository_name(repository_name: BaseModelRepository) -> str:
    return re.sub(
        r'(?<!^)(?=[A-Z])',
        '_',
        repository_name.__name__
    ).lower()


def provide_model_repository(*repositories: list[BaseModelRepository]):
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            return await func(
                *args, **(kwargs | {
                    _convert_repository_name(repository_name=r): r()
                    for r in repositories
                })
            )
        return wrapped
    return wrapper
