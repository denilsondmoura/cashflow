from pydantic import BaseModel
from cashflow.domain.objects_values import Currency

class BudgetItemDTO(BaseModel):
    id: int
    description: str
    amount_formatted: str
    amount_raw: str