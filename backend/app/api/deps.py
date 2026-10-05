import uuid
from typing import Callable, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.schemas.auth import SubjectContext
from app.services.auth_service import get_user_by_id

security_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )
    return user


def get_current_user_context(
    current_user: User = Depends(get_current_user),
) -> SubjectContext:
    """
    Extracts SubjectContext for policy evaluation and authorization-aware retrieval.
    """
    return SubjectContext(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        clearance_level=current_user.clearance_level,
        department=current_user.department,
    )


def require_role(*allowed_roles: UserRole | str) -> Callable[[User], User]:
    """
    RBAC dependency factory that validates if the current user belongs to the allowed roles.
    """
    normalized_roles = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role in: {normalized_roles}, current: {current_user.role}",
            )
        return current_user

    return role_checker


def require_clearance(min_clearance_level: int) -> Callable[[User], User]:
    """
    Clearance hierarchy dependency factory that validates user has sufficient clearance tier.
    """
    def clearance_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.clearance_level < min_clearance_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Minimum clearance level {min_clearance_level} required; current: {current_user.clearance_level}",
            )
        return current_user

    return clearance_checker
