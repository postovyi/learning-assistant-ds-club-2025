from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service
from app.services.auth_service import AuthService
from app.dto.user import UserCreate, UserRead

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.register_user(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        password=user_in.password
    )
    return user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.authenticate_user(form_data.username, form_data.password)
