from pydantic import BaseModel, Field
from decimal import Decimal


class CreateBudgetPlanningCommand(BaseModel):
    planning_id: int
    current_balance: Decimal
    limit_amount: Decimal
    description: str = Field(min_length=2)


class UpdateBudgetPlanningCommand(BaseModel):
    id: int
    current_balance: Decimal
    limit_amount: Decimal
    description: str = Field(min_length=2)