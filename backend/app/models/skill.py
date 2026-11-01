from sqlalchemy import String, Enum as SQLEnum, DateTime, func, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
from enum import Enum as PyEnum

from app.core.database import Base


class SkillCategory(str, PyEnum):
    GENETICS = "genetics"
    BIOINFORMATICS = "bioinformatics"
    MACHINE_LEARNING = "machine-learning"
    DATA_ANALYSIS = "data-analysis"
    VISUALIZATION = "visualization"
    WORKFLOW = "workflow"
    OTHER = "other"


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[SkillCategory] = mapped_column(SQLEnum(SkillCategory), default=SkillCategory.OTHER, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_url: Mapped[str] = mapped_column(String(500), nullable=True)
    documentation_url: Mapped[str] = mapped_column(String(500), nullable=True)
    parameters_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    returns_schema: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "author": self.author,
            "repository_url": self.repository_url,
            "documentation_url": self.documentation_url,
            "parameters_schema": self.parameters_schema,
            "returns_schema": self.returns_schema,
            "tags": self.tags,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
