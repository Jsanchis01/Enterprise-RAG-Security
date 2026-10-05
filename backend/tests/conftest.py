import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole, ClearanceLevel, Department
from app.api.deps import get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Ensure all tables exist before running test suite.
    """
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """
    Provides a database session for testing, with transaction cleanup.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Provides a FastAPI TestClient with the get_db dependency overridden to use the test session.
    """
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db: Session) -> User:
    user = User(
        username="test_admin_user",
        email="test_admin@enterprise.internal",
        hashed_password=hash_password("AdminPass123!"),
        role=UserRole.ADMIN.value,
        clearance_level=ClearanceLevel.RESTRICTED.value,
        department=Department.ENGINEERING.value,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_intern_user(db: Session) -> User:
    user = User(
        username="test_intern_user",
        email="test_intern@enterprise.internal",
        hashed_password=hash_password("InternPass123!"),
        role=UserRole.INTERN.value,
        clearance_level=ClearanceLevel.PUBLIC.value,
        department=Department.LEGAL.value,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_analyst_user(db: Session) -> User:
    user = User(
        username="test_analyst_user",
        email="test_analyst@enterprise.internal",
        hashed_password=hash_password("AnalystPass123!"),
        role=UserRole.ANALYST.value,
        clearance_level=ClearanceLevel.CONFIDENTIAL.value,
        department=Department.FINANCE.value,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(test_admin_user: User) -> str:
    return create_access_token(
        {
            "sub": str(test_admin_user.id),
            "username": test_admin_user.username,
            "role": test_admin_user.role,
            "clearance_level": test_admin_user.clearance_level,
            "department": test_admin_user.department,
        }
    )


@pytest.fixture
def intern_token(test_intern_user: User) -> str:
    return create_access_token(
        {
            "sub": str(test_intern_user.id),
            "username": test_intern_user.username,
            "role": test_intern_user.role,
            "clearance_level": test_intern_user.clearance_level,
            "department": test_intern_user.department,
        }
    )


@pytest.fixture
def analyst_token(test_analyst_user: User) -> str:
    return create_access_token(
        {
            "sub": str(test_analyst_user.id),
            "username": test_analyst_user.username,
            "role": test_analyst_user.role,
            "clearance_level": test_analyst_user.clearance_level,
            "department": test_analyst_user.department,
        }
    )
