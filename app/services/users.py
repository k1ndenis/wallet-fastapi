from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repository import users as users_repository
from app.schemas import UserResponse
from app.utils.auth import get_password_hash, verify_password

def create_user(db: Session, login: str, password: str) -> UserResponse:
    if users_repository.get_user_by_login(db, login):
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(password)
    user = users_repository.create_user(db, login, hashed_password)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)

def authenticate_user(db: Session, login: str, password: str) -> UserResponse:
    user = users_repository.get_user_by_login(db, login)
    print(f"User found: {user is not None}")
    if user:
        print(f"Password match: {verify_password(password, user.hashed_password)}")
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return UserResponse.model_validate(user)