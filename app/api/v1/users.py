from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependency import get_db
from app.schemas import UserRequest, UserResponse, LoginRequest, TokenResponse
from app.services import users as users_service
from app.utils.auth import create_access_token, get_current_user
from app.models import User

router = APIRouter()

@router.post("/users", response_model=UserResponse)
def create_user(payload: UserRequest, db: Session = Depends(get_db)):
    return users_service.create_user(db, payload.login, payload.password)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = users_service.authenticate_user(db, payload.login, payload.password)
    access_token = create_access_token(data={"sub": user.login})
    return TokenResponse(access_token=access_token, user=user)

@router.get("/users/me", response_model=UserResponse)
def get_current_user(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)