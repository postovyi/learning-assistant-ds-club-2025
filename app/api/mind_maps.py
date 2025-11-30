from uuid import UUID
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_mind_map_service
from app.models.user import User
from app.services.mind_map_service import MindMapService
from app.dto.content import MindMapRead

router = APIRouter()

@router.post("/sessions/{session_id}/mind-maps", response_model=MindMapRead)
async def generate_mind_map(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    mind_map_service: MindMapService = Depends(get_mind_map_service)
):
    return await mind_map_service.generate_mind_map(session_id, current_user.id)

@router.get("/sessions/{session_id}/mind-maps", response_model=list[MindMapRead])
async def get_session_mind_maps(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    mind_map_service: MindMapService = Depends(get_mind_map_service)
):
    return await mind_map_service.get_session_mind_maps(session_id, current_user.id)
