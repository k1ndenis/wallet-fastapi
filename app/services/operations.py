from fastapi import HTTPException

from app.schemas import OperationRequest
from app.repository import wallets as wallets_repository

def add_income(operation: OperationRequest):
	if wallets_repository.is_wallet_exist(operation.wallet_name):
		raise HTTPException(
			status_code=404,
			detail=f"Wallet: '{operation.wallet_name}' not found"
		)
	new_balance = wallets_repository.add_income(operation.wallet_name, operation.amount)
	return {
		"message": "Income added",
		"wallet": operation.wallet_name,
		"amount": operation.amount,
		"description": operation.description,
		"new_balance": new_balance
	}

def add_expense(operation: OperationRequest):
	# проверка на существование кошелька
	if wallets_repository.is_wallet_exist(operation.wallet_name):
		raise HTTPException(
			status_code=404,
			detail=f"Wallet '{operation.wallet_name}' not found"
		)
	# проверка на положительную сумму
	balance = wallets_repository.get_wallet_balance_by_name(operation.wallet_name)
	# проверка на кол-во средств
	if balance < operation.amount:
		raise HTTPException(
			status_code=400,
			detail=f"Insufficient funds. Availible: {balance}"
		)
	# вычитание расход из баланса
	new_balance = wallets_repository.add_expense(wallet_name=operation.wallet_name, amount=operation.amount)
	# возвращение информации о трате
	return {
		"message": "Expense added",
		"wallet": operation.wallet_name,
		"amount": operation.amount,
		"description": operation.description,
		"new_balance": new_balance
	}