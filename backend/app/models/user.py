import uuid
from enum import Enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    EMPLOYEE = "employee"
    INTERN = "intern"


class ClearanceLevel(int, Enum):
    PUBLIC = 1
    INTERNAL = 2
    CONFIDENTIAL = 3
    RESTRICTED = 4


class Department(str, Enum):
    HR = "hr"
    FINANCE = "finance"
    ENGINEERING = "engineering"
    LEGAL = "legal"


# Standard default clearance mappings
ROLE_CLEARANCE_DEFAULTS = {
    UserRole.INTERN: ClearanceLevel.PUBLIC.value,        # Level 1
    UserRole.EMPLOYEE: ClearanceLevel.INTERNAL.value,    # Level 2
    UserRole.ANALYST: ClearanceLevel.CONFIDENTIAL.value, # Level 3
    UserRole.ADMIN: ClearanceLevel.RESTRICTED.value,     # Level 4
}


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=UserRole.EMPLOYEE.value)
    clearance_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=ClearanceLevel.INTERNAL.value
    )
    department: Mapped[str] = mapped_column(String(50), nullable=False, default=Department.ENGINEERING.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<User {self.username} (role={self.role}, clearance={self.clearance_level}, dept={self.department})>"
