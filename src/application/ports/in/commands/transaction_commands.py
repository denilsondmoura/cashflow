from src.domain.objects_values import Currency
from datetime import date
from dataclasses import dataclass

@dataclass
class CreateRecurringTransactionPlanningCommand:
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

        if self.repeat and (not self.iterations or self.iterations < 2):
            raise ValueError("Quantidade de repetições da transação inválida!")

        if self.repeat and (not self.repeat_until or self.repeat_until < self.due_date):
            raise ValueError("Data de repetição da transação inválida!")  


@dataclass
class UpdateTransactionPlanningCommand:
    id: int
    data_prevista: date
    descricao: str
    valor: Currency
    foi_concluida: bool
    data_conclusao: date
    categoria: Categoria
    eh_debito_automatico: bool
    repetir: bool
    qtd_repeticoes: int
    repetir_ate: date

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


