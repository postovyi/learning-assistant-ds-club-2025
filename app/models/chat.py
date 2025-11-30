from datetime import datetime
from uuid import UUID
from sqlalchemy import ForeignKey, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseId
from app.enums.db_enums import MessageRole

class Session(BaseId):
    __tablename__ = "sessions"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    materials: Mapped[list["Material"]] = relationship("Material", back_populates="session")
    mind_maps: Mapped[list["MindMap"]] = relationship("MindMap", back_populates="session")
    homeworks: Mapped[list["Homework"]] = relationship("Homework", back_populates="session")
    lessons: Mapped[list["Lesson"]] = relationship("Lesson", back_populates="session")

class ChatMessage(BaseId):
    __tablename__ = "chat_messages"

    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"))
    role: Mapped[MessageRole] = mapped_column(SAEnum(MessageRole, values_callable=lambda obj: [e.value for e in obj]))
    content: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    session: Mapped["Session"] = relationship("Session", back_populates="messages")
