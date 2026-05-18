from decimal import Decimal
from app.models import Wallet
from app.enum import CurrencyEnum

def test_transfer_success_same_currency(db_session, client, test_user):
    from_wallet = Wallet(name="from_rub", balance=Decimal('500'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    to_wallet = Wallet(name="to_rub", balance=Decimal('0'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([from_wallet, to_wallet])
    db_session.commit()
    db_session.refresh(from_wallet)
    db_session.refresh(to_wallet)

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": 100
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "transfer"
    assert Decimal(data["amount"]) == Decimal('100')
    assert "Transfer to wallet" in data["category"]

    db_session.refresh(from_wallet)
    db_session.refresh(to_wallet)
    assert from_wallet.balance == Decimal('400')
    assert to_wallet.balance == Decimal('100')

def test_transfer_success_different_currency(db_session, client, test_user):
    from_wallet = Wallet(name="from_usd", balance=Decimal('100'), currency=CurrencyEnum.USD, user_id=test_user.id)
    to_wallet = Wallet(name="to_rub", balance=Decimal('0'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([from_wallet, to_wallet])
    db_session.commit()
    db_session.refresh(from_wallet)
    db_session.refresh(to_wallet)

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": 10
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "transfer"

    db_session.refresh(from_wallet)
    assert from_wallet.balance == Decimal('90')

def test_transfer_insufficient_funds(db_session, client, test_user):
    from_wallet = Wallet(name="from", balance=Decimal('50'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    to_wallet = Wallet(name="to", balance=Decimal('0'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([from_wallet, to_wallet])
    db_session.commit()

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": 100
        }
    )
    assert response.status_code == 400
    assert "Not enough money" in response.json()["detail"]

def test_transfer_from_wallet_not_found(db_session, client, test_user):
    to_wallet = Wallet(name="to", balance=Decimal('0'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(to_wallet)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": 999,
            "to_wallet_id": to_wallet.id,
            "amount": 10
        }
    )
    assert response.status_code == 404

def test_transfer_to_wallet_not_found(db_session, client, test_user):
    from_wallet = Wallet(name="from", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(from_wallet)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": 999,
            "amount": 10
        }
    )
    assert response.status_code == 404

def test_transfer_negative_amount(db_session, client, test_user):
    from_wallet = Wallet(name="from", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    to_wallet = Wallet(name="to", balance=Decimal('0'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([from_wallet, to_wallet])
    db_session.commit()

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": -10
        }
    )
    assert response.status_code == 422

def test_transfer_same_wallet(db_session, client, test_user):
    wallet = Wallet(name="same", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": wallet.id,
            "to_wallet_id": wallet.id,
            "amount": 10
        }
    )
    assert response.status_code == 422