from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

app = FastAPI()

BALANCE = {}

class OperationRequest(BaseModel):
	wallet_name: str
	amount: float
	description: str | None = None

@app.get("/balance")
def get_balance(wallet_name: str | None = None):
	if wallet_name is None:
		return {"total_balance": sum(BALANCE.values())}
	if wallet_name not in BALANCE:
		raise HTTPException(
			status_code=404,
			detail=f"Wallet '{wallet_name}' not found"
		)
	
	return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}

@app.post("/wallets/{name}")
def create_wallet(name: str, initial_balance: float = 0):
	# проверка на существование кошелька
	if name in BALANCE:
		raise HTTPException(
			status_code=400,
			detail=f"Wallet '{name}' arleady exists"
		)
	# создание кошелька
	BALANCE[name] = initial_balance
	# возвращение информации о кошельке
	return {
		"message": f"Wallet '{name} created",
		"wallet": name,
		"balance": BALANCE[name]
	}

@app.post("/operations/income")
def add_income(operation: OperationRequest):
	# проверка на существование кошелька
	if operation.wallet_name not in BALANCE:
		raise HTTPException(
			status_code=404,
			detail=f"Wallet: '{operation.wallet_name}' not found"
		)
	# проверка на положительную сумму
	if operation.amount <= 0:
		raise HTTPException(
			status_code=400,
			detail="Amount must be positive"
		)
	# добавление дохода к балансу
	BALANCE[operation.wallet_name] += operation.amount
	# возвращение информации о доходе
	return {
		"message": "Income added",
		"wallet": operation.wallet_name,
		"amount": operation.amount,
		"description": operation.description,
		"new_balance": BALANCE[operation.wallet_name]
	}

@app.post("/operations/expense")
def add_expense(operation: OperationRequest):
	# проверка на существование кошелька
	if operation.wallet_name not in BALANCE:
		raise HTTPException(
			status_code=404,
			detail=f"Wallet '{operation.wallet_name}' not found"
		)
	# проверка на положительную сумму
	if operation.amount <= 0:
		raise HTTPException(
			status_code=400,
			detail="Amount must be positive"
		)
	# проверка на кол-во средств
	if BALANCE[operation.wallet_name] < operation.amount:
		raise HTTPException(
			status_code=400,
			detail=f"Insufficient funds. Availible: {BALANCE[operation.wallet_name]}"
		)
	# вычитание расход из баланса
	BALANCE[operation.wallet_name] -= operation.amount
	# возвращение информации о трате
	return {
		"message": "Expense added",
		"wallet": operation.wallet_name,
		"amount": operation.amount,
		"description": operation.description,
		"new_balance": BALANCE[operation.wallet_name]
	}