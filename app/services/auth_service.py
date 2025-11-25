from app.repos.user_repo import UserRepo
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from fastapi import HTTPException, status

class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def register_user(self, email: str, first_name: str, last_name: str, password: str) -> User:
        """Register a new user."""
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        hashed_password = get_password_hash(password)
        user = await self.user_repo.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hashed_password
        )
        return user

    async def authenticate_user(self, email: str, password: str) -> dict:
        """Authenticate user and return access token."""
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
