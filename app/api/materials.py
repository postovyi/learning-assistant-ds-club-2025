from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File

from app.api.deps import get_current_user, get_material_service
from app.models.user import User
from app.services.material_service import MaterialService
from app.dto.content import MaterialRead

router = APIRouter()

@router.post("/sessions/{session_id}/materials", response_model=MaterialRead)
async def upload_material(
    session_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    material_service: MaterialService = Depends(get_material_service)
):
    return await material_service.upload_material(session_id, current_user.id, file)

@router.get("/sessions/{session_id}/materials", response_model=list[MaterialRead])
async def get_materials(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    material_service: MaterialService = Depends(get_material_service)
):
    return await material_service.get_session_materials(session_id, current_user.id)
