from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, Union

from pydantic import BaseModel

TransactionId = int


class TransactionInput(BaseModel):
    client_id: int
    transaction_timestamp: Optional[datetime]
    value: Union[Decimal, int]
    description: Optional[str]


class TransactionOutput(BaseModel):
    transaction_id: Optional[int]
    message: str


class GetBalanceOutput(BaseModel):
    balance: Decimal


class Error(BaseModel):
    reason: Literal["BAD_REQUEST", "CONFLICT", "UNKNOWN", "NOT_FOUND"]
    message: str
    status_code: int


class GetVolumeFinancialInput(BaseModel):
    client_id: int
    date_initial: Optional[datetime]
    date_end: Optional[datetime]


class Transactions(BaseModel):
    client_id: int
    transaction_timestamp: datetime
    value: Decimal
    description: Optional[str]


class HistoricOutput(BaseModel):
    transactions: list[Transactions]
