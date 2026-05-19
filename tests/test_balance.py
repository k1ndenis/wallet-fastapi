from decimal import Decimal

def test_get_balance_empty(client, test_user_with_token):
    response = client.get(
        "/api/v1/balance",
        headers={"Authorization": f"Bearer {test_user_with_token}"}
    )
    assert response.status_code == 200
    assert Decimal(response.json()["total_balance"]) == Decimal('0')

def test_get_balance_single_wallet(client, test_user_with_token, test_wallet):
    response = client.get(
        "/api/v1/balance",
        headers={"Authorization": f"Bearer {test_user_with_token}"}
    )
    assert response.status_code == 200
    assert Decimal(response.json()["total_balance"]) == test_wallet.balance

def test_get_balance_unauthorized(client):
    from main import app
    from app.dependency import get_current_user
    
    def mock_unauthorized():
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    app.dependency_overrides[get_current_user] = mock_unauthorized
    
    response = client.get("/api/v1/balance")
    assert response.status_code == 401
    
    from tests.conftest import mock_get_current_user
    app.dependency_overrides[get_current_user] = mock_get_current_user