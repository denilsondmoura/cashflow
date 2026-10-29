from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field, model_validator

class CreateRecurringTransactionToPlanningCommand(BaseModel):
    planning_id: int
    due_date: date
    description: str = Field(min_length=3)
    amount: Decimal = Field(ge=Decimal(0))
    type: str
    cleared: bool
    auto_pay: bool
    repeat: bool
    repeat_until: date | None = None
    iterations: int | None = None

    @classmethod
    def from_request(cls, request, planning_id) -> 'CreateRecurringTransactionToPlanningCommand': 
        data = request.POST.dict()
        data['planning_id'] = planning_id
        data['due_date'] = data.get('due_date') or None
        data['description'] = data.get('description') or None
        amount_str = data.get('amount') or None
        clean_amount = amount_str.replace('.', '').replace(',', '.')
        data['amount'] = Decimal(clean_amount)
        data['type'] = data.get('type') or None  # 'inflow' or 'outflow'
        data['cleared'] = data.get('cleared') == 'on' or data.get('cleared') == 'true'
        data['auto_pay'] = data.get('auto_pay') == 'on' or data.get('auto_pay') == 'true'
        data['repeat'] = data.get('repeat') == 'on' or data.get('repeat') == 'true'
        data['repeat_until'] = data.get('repeat_until') or None
        data['iterations'] = data.get('iterations') or None

        return cls(**data)

    @model_validator(mode='after')
    def _validate_recurring_rules(self):
        if not self.repeat:
            return self

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


