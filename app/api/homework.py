from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File
from app.api.deps import get_current_user, get_homework_service
from app.models.user import User
from app.services.homework_service import HomeworkService
from app.dto.content import HomeworkRead, HomeworkCreate, HomeworkTaskRead

router = APIRouter()

@router.post("/sessions/{session_id}/homework", response_model=HomeworkRead)
async def create_homework(
    session_id: UUID,
    data: HomeworkCreate,
    current_user: User = Depends(get_current_user),
    homework_service: HomeworkService = Depends(get_homework_service)
):
    return await homework_service.create_homework(session_id, current_user.id, data)

@router.get("/sessions/{session_id}/homework", response_model=list[HomeworkRead])
async def get_session_homeworks(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    homework_service: HomeworkService = Depends(get_homework_service)
):
    return await homework_service.get_session_homeworks(session_id, current_user.id)

@router.get("/homework/{homework_id}", response_model=HomeworkRead)
async def get_homework(
    homework_id: UUID,
    current_user: User = Depends(get_current_user),
    homework_service: HomeworkService = Depends(get_homework_service)
):
    return await homework_service.get_homework(homework_id, current_user.id)

@router.post("/homework/{homework_id}/tasks/{task_id}/upload", response_model=HomeworkTaskRead)
async def upload_task_solution(
    homework_id: UUID,
    task_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    homework_service: HomeworkService = Depends(get_homework_service)
):
    return await homework_service.upload_task_solution(homework_id, task_id, current_user.id, file)

@router.post("/homework/{homework_id}/submit", response_model=HomeworkRead)
async def submit_homework(
    homework_id: UUID,
    current_user: User = Depends(get_current_user),
    homework_service: HomeworkService = Depends(get_homework_service)
):
    return await homework_service.submit_homework(homework_id, current_user.id)
