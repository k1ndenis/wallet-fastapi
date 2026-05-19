from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Generator
from sqlalchemy.orm import Session
from jose import jwt

from app.database import SessionLocal
from app.models import User
from app.repository import users as users_repository

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login = payload.get("sub")
        if not login:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = users_repository.get_user_by_login(db, login)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user