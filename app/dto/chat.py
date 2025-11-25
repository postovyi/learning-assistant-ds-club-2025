from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums.db_enums import MessageRole

class MessageBase(BaseModel):
    role: MessageRole
    content: str

class MessageCreate(MessageBase):
    pass

class MessageRead(MessageBase):
    id: UUID
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SessionBase(BaseModel):
    title: str

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
