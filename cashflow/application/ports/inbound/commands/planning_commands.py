from datetime import date
from dataclasses import dataclass


@dataclass
class CreatePlanningCommand:
    name: str
    end_date: date
    start_billing_cycle: int
    created_by: str

    def __post_init__(self):
        if not self.end_date:
            raise ValueError("Data final do planejamento não informada!")        

        if not self.name or not self.name.strip():
            raise ValueError("Nome do planejamento não informado!")

        if not self.start_billing_cycle:
            raise ValueError("Dia de início do ciclo de faturamento não informado!")


@dataclass
class UpdatePlanningCommand:
    id: int
    name: str
    end_date: date
    start_billing_cycle: int
    updated_by: str

    def __post_init__(self):
        if not self.end_date:
            raise ValueError("Data final do planejamento não informada!")        

        if not self.name or not self.name.strip():
            raise ValueError("Nome do planejamento não informado!")

        if not self.start_billing_cycle:
            raise ValueError("Dia de início do ciclo de faturamento não informado!")
