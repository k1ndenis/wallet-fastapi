from decimal import Decimal
from app.models import Wallet
from app.enum import CurrencyEnum

def test_add_expense_success(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('200'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": wallet.name,
            "amount": 50.0,
            "currency": "rub",
            "description": "Food"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "expense"
    assert Decimal(data["amount"]) == Decimal('50')
    assert data["category"] == "Food"
    assert data["currency"] == "rub"
    assert data["wallet_id"] == wallet.id

    db_session.refresh(wallet)
    assert wallet.balance == Decimal('150')

def test_add_expense_insufficient_funds(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('30'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": wallet.name,
            "amount": 50.0,
            "currency": "rub",
            "description": "Expensive"
        }
    )
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]

def test_add_expense_wallet_not_found(client, test_user):
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "nonexistent",
            "amount": 50.0,
            "currency": "rub",
            "description": "Food"
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_add_expense_negative_amount(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('200'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": wallet.name,
            "amount": -50.0,
            "currency": "rub",
            "description": "Food"
        }
    )
    assert response.status_code == 422

def test_add_expense_zero_amount(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('200'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": wallet.name,
            "amount": 0,
            "currency": "rub",
            "description": "Free"
        }
    )
    assert response.status_code == 422

def test_add_expense_empty_wallet_name(client, test_user):
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "   ",
            "amount": 50.0,
            "currency": "rub",
            "description": "Food"
        }
    )
    assert response.status_code == 422

def test_add_expense_exact_balance(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('50'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": wallet.name,
            "amount": 50.0,
            "currency": "rub",
            "description": "Exact"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert Decimal(data["amount"]) == Decimal('50')
    assert data["type"] == "expense"
    assert data["category"] == "Exact"

    db_session.refresh(wallet)
    assert wallet.balance == Decimal('0')