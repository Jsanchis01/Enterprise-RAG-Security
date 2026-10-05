import uuid
from datetime import datetime, timezone
from typing import Any, List
from sqlalchemy import String, Integer, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    subject_role: Mapped[str] = mapped_column(String(50), nullable=True)
    subject_department: Mapped[str] = mapped_column(String(50), nullable=True)
    max_clearance_level: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Stored as JSONB in PostgreSQL or JSON for dialect compatibility
    allowed_departments: Mapped[List[str]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    allowed_classifications: Mapped[List[str]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    required_trust_statuses: Mapped[List[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=["certified"]
    )

    effect: Mapped[str] = mapped_column(String(20), default="ALLOW", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
