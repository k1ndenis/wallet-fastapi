from fastapi import FastAPI

from app.database import Base, engine
from app.api.v1.wallets import router as wallets_router
from app.api.v1.operations import router as operations_router
from app.api.v1.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(wallets_router, prefix="/api/v1", tags=["wallets"])
app.include_router(operations_router, prefix="/api/v1", tags=["operatons"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])