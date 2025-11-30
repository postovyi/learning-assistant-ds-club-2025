from uuid import UUID
from fastapi import HTTPException
from app.repos.chat_repo import SessionRepo, ChatMessageRepo
from app.models.chat import Session, ChatMessage
from app.services.conversational_agent import ConversationalAgent
from app.enums.db_enums import MessageRole

from app.services.vector_store import VectorStoreService

class ChatService:
    def __init__(
        self,
        session_repo: SessionRepo,
        message_repo: ChatMessageRepo,
        agent_service: ConversationalAgent,
        vector_store_service: VectorStoreService
    ):
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.agent_service = agent_service
        self.vector_store_service = vector_store_service

    async def create_session(self, user_id: UUID, title: str) -> Session:
        """Create a new learning session for a user."""
        return await self.session_repo.create(user_id=user_id, title=title)

    async def get_user_sessions(self, user_id: UUID) -> list[Session]:
        """Get all sessions for a user."""
        return await self.session_repo.get_by_user(user_id)

    async def send_message(self, session_id: UUID, user_id: UUID, content: str) -> ChatMessage:
        """Send a message in a session and get agent response."""
        # Verify session belongs to user
        session = await self.session_repo.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")

        # Save user message
        await self.message_repo.create(
            session_id=session_id,
            role=MessageRole.USER,
            content=content
        )

        # Get vector store ID
        vector_store_name = f"session_{session_id}"
        vector_store_id = await self.vector_store_service.get_or_create_vector_store(vector_store_name)

        # Get agent response
        response_text = await self.agent_service.send_message(
            session_id=str(session_id),
            message=content,
            vector_store_id=vector_store_id
        )

        # Save agent response
        agent_message = await self.message_repo.create(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=response_text
        )

        return agent_message

    async def get_session_messages(self, session_id: UUID, user_id: UUID) -> list[ChatMessage]:
        """Get all messages in a session."""
        # Verify session belongs to user
        session = await self.session_repo.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return await self.message_repo.get_by_session(session_id)
    
    async def clear_session_on_logout(self, user_id: UUID) -> None:
        """Clear all messages from all user sessions on logout."""
        sessions = await self.session_repo.get_by_user(user_id)
        for session in sessions:
            await self.message_repo.clear_session_messages(session.id)
