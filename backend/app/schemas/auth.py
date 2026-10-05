import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole, ClearanceLevel, Department, ROLE_CLEARANCE_DEFAULTS


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    department: Department = Department.ENGINEERING


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    role: str
    clearance_level: int
    department: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str
    username: str
    role: str
    clearance_level: int
    department: str
    exp: int


class SubjectContext(BaseModel):
    """
    Security and authorization context extracted from the validated subject.
    Passed directly into the PolicyEngine and retrieval services.
    """
    user_id: uuid.UUID
    username: str
    role: str
    clearance_level: int
    department: str
