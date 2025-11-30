import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.repos.user_repo import UserRepo
from app.models.user import User
from app.services.conversational_agent import ConversationalAgent
from app.services.vector_store import VectorStoreService

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ... imports

security = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepo(User, db)
    user = await user_repo.get_by_email(email)
    if user is None:
        raise credentials_exception
    return user

async def get_agent_service() -> ConversationalAgent:
    # The openai-agents SDK handles the client internally
    return ConversationalAgent()

async def get_vector_store_service() -> VectorStoreService:
    return VectorStoreService()

# Repository dependencies
async def get_user_repo(db: AsyncSession = Depends(get_db)):
    from app.repos.user_repo import UserRepo
    from app.models.user import User
    return UserRepo(User, db)

async def get_session_repo(db: AsyncSession = Depends(get_db)):
    from app.repos.chat_repo import SessionRepo
    from app.models.chat import Session
    return SessionRepo(Session, db)

async def get_chat_message_repo(db: AsyncSession = Depends(get_db)):
    from app.repos.chat_repo import ChatMessageRepo
    from app.models.chat import ChatMessage
    return ChatMessageRepo(ChatMessage, db)

async def get_material_repo(db: AsyncSession = Depends(get_db)):
    from app.repos.content_repo import MaterialRepo
    from app.models.content import Material
    return MaterialRepo(Material, db)

# Service dependencies
async def get_auth_service(user_repo = Depends(get_user_repo)):
    from app.services.auth_service import AuthService
    return AuthService(user_repo)

async def get_chat_service(
    session_repo = Depends(get_session_repo),
    message_repo = Depends(get_chat_message_repo),
    agent_service: ConversationalAgent = Depends(get_agent_service),
    vector_store_service: VectorStoreService = Depends(get_vector_store_service)
):
    from app.services.chat_service import ChatService
    return ChatService(session_repo, message_repo, agent_service, vector_store_service)

async def get_material_service(
    session_repo = Depends(get_session_repo),
    material_repo = Depends(get_material_repo),
    vector_store_service: VectorStoreService = Depends(get_vector_store_service)
):
    from app.services.material_service import MaterialService
    return MaterialService(session_repo, material_repo, vector_store_service)

async def get_homework_repo(db: AsyncSession = Depends(get_db)):
    from app.repos.content_repo import HomeworkRepo
    from app.models.content import Homework
    return HomeworkRepo(Homework, db)

async def get_homework_service(
    homework_repo = Depends(get_homework_repo),
    session_repo = Depends(get_session_repo),
    material_repo = Depends(get_material_repo),
    vector_store_service: VectorStoreService = Depends(get_vector_store_service)
):
    from app.services.homework_service import HomeworkService
    return HomeworkService(homework_repo, session_repo, material_repo, vector_store_service)

async def get_mind_map_repo(db: AsyncSession = Depends(get_db)):
    from app.repos.content_repo import MindMapRepo
    from app.models.content import MindMap
    return MindMapRepo(MindMap, db)

async def get_mind_map_service(
    mind_map_repo = Depends(get_mind_map_repo),
    session_repo = Depends(get_session_repo),
    material_repo = Depends(get_material_repo),
    vector_store_service: VectorStoreService = Depends(get_vector_store_service)
):
    from app.services.mind_map_service import MindMapService
    return MindMapService(mind_map_repo, session_repo, material_repo, vector_store_service)
