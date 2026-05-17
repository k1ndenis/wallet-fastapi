from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

BALANCE = {}

class OperationRequest(BaseModel):
	wallet_name: str = Field(..., max_length=127)
	amount: float
	description: str | None = Field(None, max_length=255)

	@field_validator('amount')
	def amount_must_be_positive(cls, v: float) -> float:
		if v <= 0:
			raise ValueError("Amount must be positive")
		return v

	@field_validator('wallet_name')
	def wallet_name_not_empty(cls, v: str) -> str:
		v = v.strip()
		if not v:
			raise ValueError("Wallet name cannot be empty")
		return v

class CreateWalletRequest(BaseModel):
	name: str = Field(..., max_length=127)
	initial_balance: float = 0

	@field_validator('name')
	def name_not_empty(cls, v: str) -> str:
		v = v.strip()
		if not v:
			raise ValueError("Wallet name cannot be empty")
		return v
	
	@field_validator('initial_balance')
	def balance_not_negative(cls, v: float) -> float:
		if v < 0:
			raise ValueError("Initial balance cannot be negative")
		return v

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

@app.post("/wallets")
def create_wallet(wallet: CreateWalletRequest):
	# проверка на существование кошелька
	if wallet.name in BALANCE:
		raise HTTPException(
			status_code=400,
			detail=f"Wallet '{wallet.name}' arleady exists"
		)
	# создание кошелька
	BALANCE[wallet.name] = wallet.initial_balance
	# возвращение информации о кошельке
	return {
		"message": f"Wallet '{wallet.name}' created",
		"wallet": wallet.name,
		"balance": BALANCE[wallet.name]
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