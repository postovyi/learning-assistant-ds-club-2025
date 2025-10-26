from fastapi import APIRouter
from .chat import router as chat_router
from .auth import router as auth_router
from .homework import router as homework_router
from .lesson import router as lesson_router
from .materials import router as materials_router
from .mind_map import router as mind_map_router
from .session import router as session_router
from .user import router as user_router

router = APIRouter(prefix="/api")
router.include_router(user_router)
router.include_router(auth_router)
router.include_router(session_router)
router.include_router(materials_router)
router.include_router(chat_router)
router.include_router(homework_router)
router.include_router(lesson_router)
router.include_router(mind_map_router)