from pydantic import BaseModel
from cashflow.domain.objects_values import Currency
from datetime import date
from typing import List


class TransactionItemDTO(BaseModel):
    id: int
    due_date_str: str
    due_date_iso: str
    description: str
    amount_formatted: str
    amount_raw: str
    cleared: bool
    type: str

class TransactionsGroupedByMonthDTO(BaseModel):
    month: str
    transactions: List[TransactionItemDTO]
    total_formatted: str

