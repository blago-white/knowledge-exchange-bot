from abc import ABCMeta, abstractmethod


class BaseService:
    pass


class BaseModelService(BaseService):
    _repository: object = None

    @property
    def repository(self):
        return self._repository
