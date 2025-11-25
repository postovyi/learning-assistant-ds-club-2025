from uuid import UUID
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_chat_service
from app.models.user import User
from app.services.chat_service import ChatService
from app.dto.chat import SessionCreate, SessionRead, MessageCreate, MessageRead

router = APIRouter()

@router.post("/sessions", response_model=SessionRead)
async def create_session(
    session_in: SessionCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.create_session(current_user.id, session_in.title)

@router.get("/sessions", response_model=list[SessionRead])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.get_user_sessions(current_user.id)

@router.post("/sessions/{session_id}/messages", response_model=MessageRead)
async def send_message(
    session_id: UUID,
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.send_message(session_id, current_user.id, message_in.content)

@router.get("/sessions/{session_id}/messages", response_model=list[MessageRead])
async def get_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.get_session_messages(session_id, current_user.id)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    await chat_service.clear_session_on_logout(current_user.id)
    return {"message": "Logged out successfully, chat history cleared"}
