from cash_flow.domain.objects_values import Currency
from dataclasses import dataclass


@dataclass
class CreateBudgetPlanningCommand:
    planning_id: int
    current_balance: Currency
    limit_amount: Currency
    description: str

    def __post_init__(self):    
        if not self.description or not self.description.strip():
            raise ValueError("Descrição do orçamento não informada!")


@dataclass
class UpdateBudgetPlanningCommand:
    id: int
    current_balance: Currency
    limit_amount: Currency
    description: str

    def __post_init__(self):
        if not self.description or not self.description.strip():
            raise ValueError("Descrição do orçamento não informada!")