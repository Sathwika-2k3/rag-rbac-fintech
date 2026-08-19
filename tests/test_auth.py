from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_with_valid_credentials():
    response = client.get("/login", auth=("Natasha", "hrpass123"))
    assert response.status_code == 200
    assert response.json()["role"] == "hr"


def test_login_with_wrong_password_is_rejected():
    response = client.get("/login", auth=("Natasha", "wrongpassword"))
    assert response.status_code == 401


def test_login_with_unknown_user_is_rejected():
    response = client.get("/login", auth=("NotARealUser", "whatever"))
    assert response.status_code == 401


def test_me_endpoint_returns_role_and_allowed_departments():
    response = client.get("/me", auth=("Sid", "sidpass123"))
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "marketing"
    assert set(data["allowed_departments"]) == {"marketing", "general"}


def test_usage_endpoint_restricted_to_c_level():
    response = client.get("/usage", auth=("Sid", "sidpass123"))
    assert response.status_code == 403


def test_usage_endpoint_allowed_for_c_level():
    response = client.get("/usage", auth=("Nick", "nickpass123"))
    assert response.status_code == 200
