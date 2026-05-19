def test_create_user_duplicate(client):
    client.post("/api/v1/users", json={"login": "duplicate_user", "password": "pass123"})

    response = client.post(
        "/api/v1/users",
        json={"login": "duplicate_user", "password": "pass123"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_create_user_duplicate(client):
    client.post("/api/v1/users", json={"login": "duplicate_user", "password": "pass123"})

    response = client.post(
        "/api/v1/users",
        json={"login": "duplicate_user", "password": "pass123"}
    )
    assert response.status_code == 400

def test_create_user_empty_login(client):
    response = client.post(
        "/api/v1/users",
        json={"login": "   "}
    )
    assert response.status_code == 422

def test_get_current_user_success(client, test_user):
    login_resp = client.post(
        "/api/v1/login",
        json={"login": "test_user", "password": "testpass"}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    
    data = login_resp.json()
    assert "access_token" in data, f"No access_token in response: {data}"
    token = data["access_token"]
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["login"] == "test_user"

def test_get_current_user_unauthorized(client):
    from main import app
    from app.dependency import get_current_user
    
    def mock_unauthorized():
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    app.dependency_overrides[get_current_user] = mock_unauthorized
    
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    
    from tests.conftest import mock_get_current_user
    app.dependency_overrides[get_current_user] = mock_get_current_user

def test_login_success(client):
    client.post("/api/v1/users", json={"login": "logintest", "password": "pass123"})

    response = client.post(
        "/api/v1/login",
        json={"login": "logintest", "password": "pass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_create_user_invalid_password(client):
    response = client.post(
        "/api/v1/users",
        json={"login": "newuser", "password": "123"}
    )
    assert response.status_code == 422

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/login",
        json={"login": "test_user", "password": "wrongpass"}
    )
    assert response.status_code == 401

def test_login_user_not_found(client):
    response = client.post(
        "/api/v1/login",
        json={"login": "nonexistent", "password": "pass"}
    )
    assert response.status_code == 401

def test_get_me_unauthorized(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401