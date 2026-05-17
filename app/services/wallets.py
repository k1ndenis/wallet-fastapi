from fastapi import HTTPException

from app.schemas import CreateWalletRequest
from app.repository import wallets as wallets_repository
from app.database import SessionLocal

def get_wallet(wallet_name: str | None = None):
	db = SessionLocal()
	try:
		if wallet_name is None:
			wallets = wallets_repository.get_all_wallets(db)
			return {"total_balance": sum([w.balance for w in wallets])}
		if not wallets_repository.is_wallet_exist(db, wallet_name):
			raise HTTPException(
				status_code=404,
				detail=f"Wallet '{wallet_name}' not found"
			)
		wallet = wallets_repository.get_wallet_balance_by_name(db, wallet_name)
		return {"wallet": wallet_name, "balance": wallet.balance}
	finally:
		db.close()

def create_wallet(wallet: CreateWalletRequest):
	db = SessionLocal()
	try:
		if wallets_repository.is_wallet_exist(db, wallet.name):
			raise HTTPException(
				status_code=400,
				detail=f"Wallet '{wallet.name}' arleady exists"
			)
		new_wallet = wallets_repository.create_wallet(db, wallet.name, wallet.initial_balance)
		db.commit()
		db.refresh(new_wallet)
		return {
			"message": f"Wallet '{wallet.name}' created",
			"wallet": wallet.name,
			"balance": new_wallet.balance
		}
	finally:
		db.close()