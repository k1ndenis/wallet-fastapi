from decimal import Decimal
from app.models import Wallet
from app.enum import CurrencyEnum

def test_create_wallet_success(client):
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "my_wallet",
            "initial_balance": 100.0,
            "currency": "rub"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "my_wallet"
    assert Decimal(data["balance"]) == Decimal('100')
    assert data["currency"] == "rub"

def test_create_wallet_duplicate_name(db_session, client, test_user):
    wallet = Wallet(name="existing", balance=Decimal('0'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "existing",
            "initial_balance": 50.0,
            "currency": "rub"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_create_wallet_negative_balance(client, test_user):
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "new_wallet",
            "initial_balance": -100.0,
            "currency": "rub"
        }
    )
    assert response.status_code == 422

def test_create_wallet_empty_name(client, test_user):
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "   ",
            "initial_balance": 100.0,
            "currency": "rub"
        }
    )
    assert response.status_code == 422

def test_get_all_wallets_empty(client, test_user):
    response = client.get("/api/v1/wallets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_all_wallets_with_data(db_session, client, test_user):
    wallet1 = Wallet(name="wallet1", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    wallet2 = Wallet(name="wallet2", balance=Decimal('200'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([wallet1, wallet2])
    db_session.commit()

    response = client.get("/api/v1/wallets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [w["name"] for w in data]
    assert "wallet1" in names
    assert "wallet2" in names

def test_get_total_balance_single_wallet(db_session, client, test_user):
    wallet = Wallet(name="wallet", balance=Decimal('150'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.get("/api/v1/balance")
    assert response.status_code == 200
    data = response.json()
    assert Decimal(data["total_balance"]) == Decimal('150')

def test_get_total_balance_multiple_wallets(db_session, client, test_user):
    wallet1 = Wallet(name="w1", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    wallet2 = Wallet(name="w2", balance=Decimal('50'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([wallet1, wallet2])
    db_session.commit()

    response = client.get("/api/v1/balance")
    assert response.status_code == 200
    data = response.json()
    assert Decimal(data["total_balance"]) == Decimal('150')

def test_get_total_balance_no_wallets(client):
    response = client.get("/api/v1/balance")
    assert response.status_code == 200
    data = response.json()
    assert Decimal(data["total_balance"]) == Decimal('0')

def test_create_wallet_usd(client, test_user_with_token):
    response = client.post(
        "/api/v1/wallets",
        json={"name": "usd_wallet", "initial_balance": 100, "currency": "usd"},
        headers={"Authorization": f"Bearer {test_user_with_token}"}
    )
    assert response.status_code == 200
    assert response.json()["currency"] == "usd"

def test_create_wallet_negative_balance(client, test_user_with_token):
    response = client.post(
        "/api/v1/wallets",
        json={"name": "neg_wallet", "initial_balance": -50, "currency": "rub"},
        headers={"Authorization": f"Bearer {test_user_with_token}"}
    )
    assert response.status_code == 422

def test_create_wallet_name_too_long(client, test_user_with_token):
    long_name = "a" * 128
    response = client.post(
        "/api/v1/wallets",
        json={"name": long_name, "initial_balance": 100, "currency": "rub"},
        headers={"Authorization": f"Bearer {test_user_with_token}"}
    )
    assert response.status_code == 422