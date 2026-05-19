from decimal import Decimal
from app.models import Wallet
from app.enum import CurrencyEnum

def test_add_income_endpoint(db_session, client, test_user):
    wallet = Wallet(name="test", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/income",
        json={
            "wallet_name": "test",
            "amount": 50.0,
            "currency": "rub",
            "description": "Salary"
        }
    )
    assert response.status_code == 200
    assert response.json()["type"] == "income"

def test_add_expense_endpoint(db_session, client, test_user):
    wallet = Wallet(name="test", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "test",
            "amount": 30.0,
            "currency": "rub",
            "description": "Food"
        }
    )
    assert response.status_code == 200
    assert response.json()["type"] == "expense"

def test_get_operations_list_endpoint(db_session, client, test_user):
    wallet = Wallet(name="test", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.get("/api/v1/operations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_operations_list_filter_by_wallet_endpoint(db_session, client, test_user):
    wallet = Wallet(name="test", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.get(f"/api/v1/operations?wallet_id={wallet.id}")
    assert response.status_code == 200

def test_transfer_endpoint(db_session, client, test_user):
    from_wallet = Wallet(name="from", balance=Decimal('200'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    to_wallet = Wallet(name="to", balance=Decimal('0'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([from_wallet, to_wallet])
    db_session.commit()

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": 50.0
        }
    )
    assert response.status_code == 200
    assert response.json()["type"] == "transfer"

def test_transfer_endpoint_insufficient_funds(db_session, client, test_user):
    from_wallet = Wallet(name="from", balance=Decimal('30'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    to_wallet = Wallet(name="to", balance=Decimal('0'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([from_wallet, to_wallet])
    db_session.commit()

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": 50.0
        }
    )
    assert response.status_code == 400

def test_add_income_zero_amount(client, test_user_with_token, test_wallet):
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": test_wallet.name, "amount": 0, "currency": "rub", "description": "Zero"},
        headers={"Authorization": f"Bearer {test_user_with_token}"}
    )
    assert response.status_code == 422

def test_add_income_wallet_not_found(client, test_user_with_token):
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": "nonexistent", "amount": 100, "currency": "rub", "description": "Test"},
        headers={"Authorization": f"Bearer {test_user_with_token}"}
    )
    assert response.status_code == 404

def test_add_expense_negative_amount(client, test_user_with_token, test_wallet):
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": test_wallet.name, "amount": -50, "currency": "rub", "description": "Negative"},
        headers={"Authorization": f"Bearer {test_user_with_token}"}
    )
    assert response.status_code == 422