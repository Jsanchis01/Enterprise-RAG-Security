import uuid

from app.models.user import UserRole, ClearanceLevel


def test_registration_forces_employee_role_and_clearance(client, db):
    """
    Public registration must not allow a user to self-assign
    privileged role or clearance.
    """
    username = f"security_test_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "SecurePass123!",
            "role": "admin",
            "clearance_level": 4,
            "department": "engineering",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["role"] == UserRole.EMPLOYEE.value
    assert data["clearance_level"] == ClearanceLevel.INTERNAL.value


def test_login_returns_bearer_token(client, test_admin_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_admin_user.username,
            "password": "AdminPass123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == test_admin_user.username


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_returns_authenticated_user(client, admin_token, test_admin_user):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == test_admin_user.username
    assert data["role"] == UserRole.ADMIN.value
    assert data["clearance_level"] == ClearanceLevel.RESTRICTED.value


def test_admin_can_access_admin_endpoint(client, admin_token):
    response = client.get(
        "/api/v1/auth/test-admin",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "authorized"


def test_intern_cannot_access_admin_endpoint(client, intern_token):
    response = client.get(
        "/api/v1/auth/test-admin",
        headers={"Authorization": f"Bearer {intern_token}"},
    )

    assert response.status_code == 403


def test_analyst_can_access_l3_endpoint(client, analyst_token):
    response = client.get(
        "/api/v1/auth/test-clearance-l3",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )

    assert response.status_code == 200


def test_intern_cannot_access_l3_endpoint(client, intern_token):
    response = client.get(
        "/api/v1/auth/test-clearance-l3",
        headers={"Authorization": f"Bearer {intern_token}"},
    )

    assert response.status_code == 403


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer this-is-not-a-valid-jwt"},
    )

    assert response.status_code == 401