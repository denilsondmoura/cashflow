from pydantic import BaseModel
from typing import List
from cashflow.application.ports.inbound.dtos.budget_dto import BudgetItemDTO 
from cashflow.application.ports.inbound.dtos.transaction_dto import TransactionsGroupedByMonthDTO 

# TODO: adicionar as validação do pydantic nos DTOs e nos Commands. Ex: gt, ld, EmailStr, etc
class PlanningItemDTO(BaseModel):
    id: int
    name: str

class PlanningForecastScreenDTO(BaseModel):
    planning: PlanningItemDTO
    inflows: List[TransactionsGroupedByMonthDTO]
    outflows: List[TransactionsGroupedByMonthDTO]
    budgets: List[BudgetItemDTO]
    total_budget_formatted: str


class PlanningCashflowScreenDTO(BaseModel):
    planning: PlanningItemDTO
    months_data: List[dict]
    budgets: List[BudgetItemDTO]
    total_balance_formatted: str
    diario_val_formatted: str
    