from uuid import UUID
from sqlalchemy import select, delete
from app.repos.base_repo import BaseRepo
from app.models.chat import Session, ChatMessage

class SessionRepo(BaseRepo[Session]):
    async def get_by_user(self, user_id: UUID) -> list[Session]:
        result = await self.session.execute(select(Session).where(Session.user_id == user_id))
        return result.scalars().all()

class ChatMessageRepo(BaseRepo[ChatMessage]):
    async def get_by_session(self, session_id: UUID) -> list[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp)
        )
        return result.scalars().all()
    
    async def clear_session_messages(self, session_id: UUID) -> None:
        """Clear all messages for a session (for logout)."""
        await self.session.execute(
            delete(ChatMessage).where(ChatMessage.session_id == session_id)
        )
        await self.session.commit()
