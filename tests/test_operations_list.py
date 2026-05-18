from datetime import datetime
from decimal import Decimal
from app.models import Wallet, Operation
from app.enum import CurrencyEnum, OperationEnum

def test_get_operations_list_all_wallets(db_session, client, test_user):
    wallet1 = Wallet(name="wallet1", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    wallet2 = Wallet(name="wallet2", balance=Decimal('200'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([wallet1, wallet2])
    db_session.commit()
    db_session.refresh(wallet1)
    db_session.refresh(wallet2)

    op1 = Operation(wallet_id=wallet1.id, type=OperationEnum.INCOME, amount=Decimal('50'), currency=CurrencyEnum.RUB, category="Salary")
    op2 = Operation(wallet_id=wallet2.id, type=OperationEnum.EXPENSE, amount=Decimal('30'), currency=CurrencyEnum.RUB, category="Food")
    db_session.add_all([op1, op2])
    db_session.commit()

    response = client.get("/api/v1/operations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["type"] in ["income", "expense"]
    assert data[1]["type"] in ["income", "expense"]

def test_get_operations_list_filter_by_wallet(db_session, client, test_user):
    wallet1 = Wallet(name="wallet1", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    wallet2 = Wallet(name="wallet2", balance=Decimal('200'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add_all([wallet1, wallet2])
    db_session.commit()
    db_session.refresh(wallet1)
    db_session.refresh(wallet2)

    op1 = Operation(wallet_id=wallet1.id, type=OperationEnum.INCOME, amount=Decimal('50'), currency=CurrencyEnum.RUB, category="Salary")
    op2 = Operation(wallet_id=wallet2.id, type=OperationEnum.EXPENSE, amount=Decimal('30'), currency=CurrencyEnum.RUB, category="Food")
    db_session.add_all([op1, op2])
    db_session.commit()

    response = client.get(f"/api/v1/operations?wallet_id={wallet1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["wallet_id"] == wallet1.id
    assert data[0]["type"] == "income"

def test_get_operations_list_wallet_not_found(db_session, client, test_user):
    response = client.get("/api/v1/operations?wallet_id=999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_operations_list_filter_by_date(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    op1 = Operation(
        wallet_id=wallet.id, type=OperationEnum.INCOME, amount=Decimal('50'),
        currency=CurrencyEnum.RUB, category="Salary", created_at=datetime(2025, 1, 15)
    )
    op2 = Operation(
        wallet_id=wallet.id, type=OperationEnum.EXPENSE, amount=Decimal('20'),
        currency=CurrencyEnum.RUB, category="Food", created_at=datetime(2025, 1, 20)
    )
    db_session.add_all([op1, op2])
    db_session.commit()

    date_from = datetime(2025, 1, 10)
    date_to = datetime(2025, 1, 18)

    response = client.get(
        f"/api/v1/operations?date_from={date_from.isoformat()}&date_to={date_to.isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "income"

def test_get_operations_list_no_operations(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()

    response = client.get("/api/v1/operations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_get_operations_list_date_from_only(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    op1 = Operation(
        wallet_id=wallet.id, type=OperationEnum.INCOME, amount=Decimal('50'),
        currency=CurrencyEnum.RUB, category="Salary", created_at=datetime(2025, 1, 15)
    )
    op2 = Operation(
        wallet_id=wallet.id, type=OperationEnum.EXPENSE, amount=Decimal('20'),
        currency=CurrencyEnum.RUB, category="Food", created_at=datetime(2025, 1, 20)
    )
    db_session.add_all([op1, op2])
    db_session.commit()

    date_from = datetime(2025, 1, 16)
    response = client.get(f"/api/v1/operations?date_from={date_from.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "expense"

def test_get_operations_list_date_to_only(db_session, client, test_user):
    wallet = Wallet(name="my_wallet", balance=Decimal('100'), currency=CurrencyEnum.RUB, user_id=test_user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    op1 = Operation(
        wallet_id=wallet.id, type=OperationEnum.INCOME, amount=Decimal('50'),
        currency=CurrencyEnum.RUB, category="Salary", created_at=datetime(2025, 1, 15)
    )
    op2 = Operation(
        wallet_id=wallet.id, type=OperationEnum.EXPENSE, amount=Decimal('20'),
        currency=CurrencyEnum.RUB, category="Food", created_at=datetime(2025, 1, 20)
    )
    db_session.add_all([op1, op2])
    db_session.commit()

    date_to = datetime(2025, 1, 16)
    response = client.get(f"/api/v1/operations?date_to={date_to.isoformat()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "income"