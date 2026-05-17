from fastapi import APIRouter, HTTPException

from app.schemas import OperationRequest
from app.services import operations as operations_service
from app.services import wallets as wallets_service

router = APIRouter()

@router.post("/operations/income")
def add_income(operation: OperationRequest):
    return operations_service.add_income(operation)
	

@router.post("/operations/expense")
def add_expense(operation: OperationRequest):
	return operations_service.add_expense(operation)