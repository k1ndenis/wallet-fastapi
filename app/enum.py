from enum import StrEnum, auto

class CurrencyEnum(StrEnum):
    RUB = auto()
    USD = auto()
    EUR = auto()

class OperationEnum(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"