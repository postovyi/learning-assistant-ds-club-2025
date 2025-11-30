from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.repos.base_repo import BaseRepo
from app.models.content import Material, MindMap, Homework, Lesson, HomeworkTask

class MaterialRepo(BaseRepo[Material]):
    async def get_by_session(self, session_id: UUID) -> list[Material]:
        result = await self.session.execute(select(Material).where(Material.session_id == session_id))
        return result.scalars().all()

class MindMapRepo(BaseRepo[MindMap]):
    async def get_by_session(self, session_id: UUID) -> list[MindMap]:
        result = await self.session.execute(select(MindMap).where(MindMap.session_id == session_id))
        return result.scalars().all()

class HomeworkRepo(BaseRepo[Homework]):
    async def get_by_session(self, session_id: UUID) -> list[Homework]:
        result = await self.session.execute(
            select(Homework)
            .where(Homework.session_id == session_id)
            .options(
                selectinload(Homework.tasks).selectinload(HomeworkTask.reviews),
                selectinload(Homework.reviews)
            )
        )
        return result.scalars().all()

    async def get(self, id: UUID) -> Homework | None:
        result = await self.session.execute(
            select(Homework)
            .where(Homework.id == id)
            .options(
                selectinload(Homework.tasks).selectinload(HomeworkTask.reviews),
                selectinload(Homework.reviews)
            )
        )
        return result.scalars().first()

class LessonRepo(BaseRepo[Lesson]):
    async def get_by_session(self, session_id: UUID) -> list[Lesson]:
        result = await self.session.execute(select(Lesson).where(Lesson.session_id == session_id))
        return result.scalars().all()
