from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

app = FastAPI()

BALANCE = {}

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