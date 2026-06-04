from pydantic import BaseModel

class BudgetItemDTO(BaseModel):
    id: int
    description: str
    amount_formatted: str
    amount_raw: str