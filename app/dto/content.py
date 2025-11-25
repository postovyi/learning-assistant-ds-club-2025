from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, HttpUrl
from app.enums.db_enums import FileType, HomeworkStatus, Grade, LessonStatus, LessonMessageType

# Material
class MaterialBase(BaseModel):
    name: str
    file_url: str
    file_type: FileType
    size: int

class MaterialCreate(MaterialBase):
    pass

class MaterialRead(MaterialBase):
    id: UUID
    session_id: UUID
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

# MindMap
class MindMapBase(BaseModel):
    title: str
    node_count: int
    data: dict[str, Any]

class MindMapCreate(MindMapBase):
    pass

class MindMapRead(MindMapBase):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Homework
class HomeworkTaskBase(BaseModel):
    task_number: int
    description: str
    uploaded_file_url: Optional[str] = None

class HomeworkTaskRead(HomeworkTaskBase):
    id: UUID
    homework_id: UUID

    model_config = ConfigDict(from_attributes=True)

class HomeworkBase(BaseModel):
    title: str
    status: HomeworkStatus

class HomeworkRead(HomeworkBase):
    id: UUID
    session_id: UUID
    generated_at: datetime
    submitted_at: Optional[datetime]
    tasks: list[HomeworkTaskRead] = []

    model_config = ConfigDict(from_attributes=True)

# Lesson
class LessonMessageBase(BaseModel):
    type: LessonMessageType
    content: str

class LessonMessageRead(LessonMessageBase):
    id: UUID
    lesson_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class LessonBase(BaseModel):
    title: str
    progress: int
    current_step: int
    total_steps: int
    status: LessonStatus

class LessonRead(LessonBase):
    id: UUID
    session_id: UUID
    created_at: datetime
    completed_at: Optional[datetime]
    messages: list[LessonMessageRead] = []

    model_config = ConfigDict(from_attributes=True)
