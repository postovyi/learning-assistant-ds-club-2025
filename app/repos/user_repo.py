from typing import Optional
from sqlalchemy import select
from app.repos.base_repo import BaseRepo
from app.models.user import User

class UserRepo(BaseRepo[User]):
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()
