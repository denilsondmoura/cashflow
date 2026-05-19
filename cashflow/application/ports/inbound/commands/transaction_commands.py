from cashflow.domain.objects_values import Currency
from datetime import date
from dataclasses import dataclass

@dataclass
class CreateRecurringTransactionPlanningCommand:
    planning_id: int
    due_date: date
    description: str
    amount: Currency
    cleared: bool
    auto_pay: bool
    repeat: bool
    repeat_until: date
    iterations: int


    def __post_init__(self):
        if not self.due_date:
            raise ValueError("Data prevista da transação não informada")
        
        if not self.description or not self.description.strip():
            raise ValueError("Descrição da transação não informada")

        if self.repeat:
            if not self.iterations and not self.repeat_until:
                raise ValueError("Defina a data limite ou a quantidade de repetições da transação!")
            
            if self.iterations is not None and self.iterations < 2:
                raise ValueError("Quantidade de repetições da transação inválida!")

            if self.repeat_until is not None and self.repeat_until < self.due_date:
                raise ValueError("Data de repetição da transação inválida!")


@dataclass
class UpdateTransactionPlanningCommand:
    id: int
    due_date: date
    description: str
    amount: Currency
    cleared: bool
    cleared_at: date
    auto_pay: bool
    repeat: bool
    iterations: int
    repeat_until: date

    def __post_init__(self):
        if not self.due_date:
            raise ValueError("Data prevista da transação não informada")
        
        if not self.description or not self.description.strip():
            raise ValueError("Descrição da transação não informada")


@dataclass
class FilterTransactionPlanningCommand:
    data_from: date
    data_to: date
    description: str
    type: str
    cleared: bool
    auto_pay: bool
