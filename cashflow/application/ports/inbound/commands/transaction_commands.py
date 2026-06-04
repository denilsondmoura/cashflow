from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field, model_validator

class CreateRecurringTransactionPlanningCommand(BaseModel):
    planning_id: int
    due_date: date
    description: str = Field(min_length=3)
    amount: Decimal
    cleared: bool
    auto_pay: bool
    repeat: bool
    repeat_until: date | None = None
    iterations: int | None = None

    @model_validator(mode='after')
    def validate_recurring_rules(self):
        if self.repeat:
            if not self.iterations and not self.repeat_until:
                raise ValueError("Defina a data limite ou a quantidade de repetições da transação!")
            
            if self.iterations is not None and self.iterations < 2:
                raise ValueError("Quantidade de repetições da transação inválida!")

            if self.repeat_until is not None and self.repeat_until < self.due_date:
                raise ValueError("Data de repetição da transação inválida!")

        return self


class UpdateTransactionPlanningCommand(BaseModel):
    id: int
    due_date: date
    description: str = Field(min_length=3)
    amount: Decimal
    cleared: bool
    auto_pay: bool
    repeat: bool
    iterations: int | None = None
    repeat_until: date | None = None

