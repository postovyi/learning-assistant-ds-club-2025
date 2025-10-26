from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, String, DateTime

class Base(DeclarativeBase):
    type_annotation_map: ClassVar = {
        UUID: postgresql.UUID,
        dict[str, Any]: postgresql.JSON,
        list[dict[str, Any]]: postgresql.ARRAY(postgresql.JSON),
        list[str]: postgresql.ARRAY(String),
        Decimal: postgresql.NUMERIC(10, 2),
        datetime: DateTime(timezone=True),
        bool: Boolean,
    }

class BaseId(Base):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)