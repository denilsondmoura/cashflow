from pydantic import BaseModel
from typing import List
from cashflow.application.ports.inbound.dtos.budget_dto import BudgetItemDTO 
from cashflow.application.ports.inbound.dtos.transaction_dto import TransactionsGroupedByMonthDTO 

class PlanningItemDTO(BaseModel):
    id: int
    name: str

class PlanningForecastScreenDTO(BaseModel):
    planning: PlanningItemDTO
    inflows: List[TransactionsGroupedByMonthDTO]
    outflows: List[TransactionsGroupedByMonthDTO]
    budgets: List[BudgetItemDTO]
    total_budget_formatted: str