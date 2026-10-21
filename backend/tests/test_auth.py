"""test_auth.py — Auth endpoint tests."""
import pytest
from tests.conftest import make_user, make_token, auth_headers


def test_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_register_user(client, db):
    resp = client.post("/api/v1/auth/register", json={
        "email": "newuser@test.com",
        "password": "strongpass123",
        "full_name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@test.com"
    assert "hashed_password" not in data


def test_register_duplicate_email(client, db):
    make_user(db, "dup@test.com")
    resp = client.post("/api/v1/auth/register", json={
        "email": "dup@test.com",
        "password": "strongpass123",
    })
    assert resp.status_code == 400


def test_login_success(client, db):
    make_user(db, "login_test@test.com", "mypassword!")
    resp = client.post("/api/v1/auth/login", json={
        "email": "login_test@test.com",
        "password": "mypassword!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db):
    make_user(db, "wrongpw@test.com", "correctpass")
    resp = client.post("/api/v1/auth/login", json={
        "email": "wrongpw@test.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_me_authenticated(client, db):
    user = make_user(db, "me_test@test.com")
    token = make_token(user)
    resp = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "me_test@test.com"


def test_me_unauthenticated(client):
    resp = client.get("/api/v1/auth/me")
    # HTTPBearer with auto_error=False returns 401 from our get_current_user dep
    assert resp.status_code in (401, 403)


def test_protected_route_bad_token(client):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer bad.token.here"})
    assert resp.status_code == 401
