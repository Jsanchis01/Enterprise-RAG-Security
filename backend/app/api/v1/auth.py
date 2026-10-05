from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token, SubjectContext
from app.services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_username,
    get_user_by_email,
    issue_token_for_user,
)
from app.api.deps import get_current_user, get_current_user_context, require_role, require_clearance

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user account with assigned role and clearance level.
    """
    if get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already registered",
        )
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered",
        )
    user = create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates username and password (Argon2), issuing a PyJWT bearer token.
    """
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    return issue_token_for_user(user)


@router.get("/me", response_model=UserResponse)
def get_current_profile(current_user: User = Depends(get_current_user)):
    """
    Returns authenticated user's profile.
    """
    return current_user


@router.get("/me/context", response_model=SubjectContext)
def get_subject_context(context: SubjectContext = Depends(get_current_user_context)):
    """
    Returns security and authorization context (SubjectContext) used for policy evaluation.
    """
    return context


@router.get("/test-admin", response_model=dict)
def test_admin_access(current_user: User = Depends(require_role(UserRole.ADMIN))):
    """
    Endpoint protected strictly by RBAC requiring 'admin' role.
    """
    return {
        "status": "authorized",
        "message": f"Welcome Admin {current_user.username}",
        "role": current_user.role,
        "clearance_level": current_user.clearance_level,
    }


@router.get("/test-clearance-l3", response_model=dict)
def test_clearance_l3_access(current_user: User = Depends(require_clearance(3))):
    """
    Endpoint protected strictly by clearance hierarchy requiring Level 3+ (Confidential/Restricted).
    """
    return {
        "status": "authorized",
        "message": f"Confidential clearance verified for {current_user.username}",
        "clearance_level": current_user.clearance_level,
    }
