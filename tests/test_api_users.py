def test_create_user_success(client):
    response = client.post(
        "/api/v1/users",
        json={"login": "new_user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "new_user"
    assert "id" in data

def test_create_user_duplicate(client):
    client.post("/api/v1/users", json={"login": "duplicate_user"})
    
    response = client.post(
        "/api/v1/users",
        json={"login": "duplicate_user"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_create_user_empty_login(client):
    response = client.post(
        "/api/v1/users",
        json={"login": "   "}
    )
    assert response.status_code == 422

def test_get_current_user_success(client, test_user):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["login"] == test_user.login

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