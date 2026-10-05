import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User, UserRole, ROLE_CLEARANCE_DEFAULTS
from app.schemas.auth import UserCreate, Token, UserResponse
from app.core.security import hash_password, verify_password, create_access_token


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=UserRole.EMPLOYEE.value,
        clearance_level=ROLE_CLEARANCE_DEFAULTS[UserRole.EMPLOYEE],
        department=(
            user_in.department.value
            if hasattr(user_in.department, "value")
            else str(user_in.department)
        ),
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def issue_token_for_user(user: User) -> Token:
    token_payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "clearance_level": user.clearance_level,
        "department": user.department,
    }
    access_token = create_access_token(data=token_payload)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
