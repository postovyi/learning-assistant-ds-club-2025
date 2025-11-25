from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Any
from sqlalchemy import ForeignKey, String, DateTime, Enum as SAEnum, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import BaseId
from app.enums.db_enums import FileType, HomeworkStatus, Grade, LessonStatus, LessonMessageType

class Material(BaseId):
    __tablename__ = "materials"

    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"))
    name: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str] = mapped_column(Text)
    file_type: Mapped[FileType] = mapped_column(SAEnum(FileType))
    size: Mapped[int] = mapped_column(Integer) # Size in bytes
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    session: Mapped["Session"] = relationship("Session", back_populates="materials")

class MindMap(BaseId):
    __tablename__ = "mind_maps"

    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"))
    title: Mapped[str] = mapped_column(String(255))
    node_count: Mapped[int] = mapped_column(Integer)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    session: Mapped["Session"] = relationship("Session", back_populates="mind_maps")

class Homework(BaseId):
    __tablename__ = "homework"

    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"))
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[HomeworkStatus] = mapped_column(SAEnum(HomeworkStatus), default=HomeworkStatus.PENDING)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped["Session"] = relationship("Session", back_populates="homeworks")
    tasks: Mapped[list["HomeworkTask"]] = relationship("HomeworkTask", back_populates="homework")
    reviews: Mapped[list["HomeworkReview"]] = relationship("HomeworkReview", back_populates="homework")

class HomeworkTask(BaseId):
    __tablename__ = "homework_tasks"

    homework_id: Mapped[UUID] = mapped_column(ForeignKey("homework.id"))
    task_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    uploaded_file_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    homework: Mapped["Homework"] = relationship("Homework", back_populates="tasks")
    reviews: Mapped[list["HomeworkTaskReview"]] = relationship("HomeworkTaskReview", back_populates="task")

class HomeworkReview(BaseId):
    __tablename__ = "homework_reviews"

    homework_id: Mapped[UUID] = mapped_column(ForeignKey("homework.id"))
    grade: Mapped[Grade | None] = mapped_column(SAEnum(Grade), nullable=True)
    overall_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    reviewed_by: Mapped[str | None] = mapped_column(String(100), nullable=True) # Could be AI or User ID

    homework: Mapped["Homework"] = relationship("Homework", back_populates="reviews")

class HomeworkTaskReview(BaseId):
    __tablename__ = "homework_task_reviews"

    homework_task_id: Mapped[UUID] = mapped_column(ForeignKey("homework_tasks.id"))
    task_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)

    task: Mapped["HomeworkTask"] = relationship("HomeworkTask", back_populates="reviews")

class Lesson(BaseId):
    __tablename__ = "lessons"

    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"))
    title: Mapped[str] = mapped_column(String(255))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer)
    status: Mapped[LessonStatus] = mapped_column(SAEnum(LessonStatus), default=LessonStatus.NOT_STARTED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped["Session"] = relationship("Session", back_populates="lessons")
    messages: Mapped[list["LessonMessage"]] = relationship("LessonMessage", back_populates="lesson")

class LessonMessage(BaseId):
    __tablename__ = "lesson_messages"

    lesson_id: Mapped[UUID] = mapped_column(ForeignKey("lessons.id"))
    type: Mapped[LessonMessageType] = mapped_column(SAEnum(LessonMessageType))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="messages")
