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

class HomeworkReviewRead(BaseModel):
    id: UUID
    grade: Optional[Grade]
    overall_feedback: Optional[str]
    reviewed_at: datetime
    reviewed_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class HomeworkTaskReviewRead(BaseModel):
    id: UUID
    task_feedback: Optional[str]
    score: Optional[Decimal]

    model_config = ConfigDict(from_attributes=True)

class HomeworkTaskRead(HomeworkTaskBase):
    id: UUID
    homework_id: UUID
    reviews: list[HomeworkTaskReviewRead] = []

    model_config = ConfigDict(from_attributes=True)

class HomeworkBase(BaseModel):
    title: str
    status: HomeworkStatus

class HomeworkCreate(BaseModel):
    prompt: str
    material_ids: list[UUID]

class HomeworkRead(HomeworkBase):
    id: UUID
    session_id: UUID
    generated_at: datetime
    submitted_at: Optional[datetime]
    tasks: list[HomeworkTaskRead] = []
    reviews: list[HomeworkReviewRead] = []

    model_config = ConfigDict(from_attributes=True)

class HomeworkTaskUpdate(BaseModel):
    uploaded_file_url: str

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
