from sqlalchemy.ext.asyncio import AsyncSession

from models.dialog import Message
from models.lesson import Subject
from repositories.base import BaseModelRepository
from repositories.dialog import DialogRepository
from repositories.lessons import LessonsModelRepository
from repositories.subjects import SubjectsModelRepository
from services.user import UserType
from .base import BaseService


class DialogsService(BaseService):
    dialogs_repository = DialogRepository()
    lessons_model_repository = LessonsModelRepository()
    subjects_model_repository = SubjectsModelRepository()

    def __init__(self, dialogs_repository: DialogRepository = None,
                 lessons_repository: LessonsModelRepository = None,
                 subjects_repository: SubjectsModelRepository = None):
        self._dialogs_repository = (dialogs_repository or
                                    self.dialogs_repository)
        self._lessons_repository = (lessons_repository or
                                    self.lessons_model_repository)
        self._subjects_repository = (subjects_repository or
                                     self.subjects_model_repository)

    @BaseModelRepository.provide_db_conn()
    async def add_message(self, session: AsyncSession,
                          sender_id: int,
                          message: Message):
        await self._can_send_message(session=session,
                                     sender_id=sender_id,
                                     sender_role=message.sender,
                                     subject_id=message.subject_id)

        await self.dialogs_repository.create(data=message)

    @BaseModelRepository.provide_db_conn()
    async def _can_send_message(self, session: AsyncSession,
                                sender_id: int,
                                sender_role: UserType,
                                subject_id: int):
        if sender_role == UserType.UNKNOWN:
            raise PermissionError("Unknown type of user")

        result: Subject = await self._subjects_repository.get(
            session=session, pk=subject_id,
            exclude_related_cols=[Subject.sell_offers,
                                  Subject.student_id
                                  if sender_role.WORKER else
                                  Subject.worker_id]
        )

        assert (
            result.worker_id == sender_id
            if sender_role == UserType.WORKER else
            result.student_id == sender_id
        ), PermissionError(
            "Cant send message, permission error"
        )
