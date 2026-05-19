import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.dependency import get_db, get_current_user
from app.database import Base
from app.models import User

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def mock_get_current_user():
    return User(id=1, login="test_user")

app.dependency_overrides[get_current_user] = mock_get_current_user

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    from app.utils.auth import get_password_hash
    user = User(login="test_user", hashed_password=get_password_hash("testpass"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user_with_token(client, test_user):
    response = client.post(
        "/api/v1/login",
        json={"login": "test_user", "password": "testpass"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return token

@pytest.fixture
def test_wallet(db_session, test_user):
    from app.models import Wallet
    from app.enum import CurrencyEnum
    from decimal import Decimal
    
    wallet = Wallet(
        name="test_wallet",
        balance=Decimal('100'),
        currency=CurrencyEnum.RUB,
        user_id=test_user.id
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    return wallet