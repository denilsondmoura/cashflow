from datetime import date
from dataclasses import dataclass


@dataclass
class CreatePlanningCommand:
    end_date: date
    name: str
    color: str

    def __post_init__(self):
        if not self.end_date:
            raise ValueError("Data final do planejamento não informada!")        

        if not self.name or not self.name.strip():
            raise ValueError("Nome do planejamento não informado!")

        if not self.color or not self.color.strip():
            raise ValueError("Cor do planejamento não informada!")


@dataclass
class UpdatePlanningCommand:
    id: int
    end_date: date
    name: str
    color: str

    def __post_init__(self):
        if not self.end_date:
            raise ValueError("Data final do planejamento não informada!")        

        if not self.name or not self.name.strip():
            raise ValueError("Nome do planejamento não informado!")

        if not self.color or not self.color.strip():
            raise ValueError("Cor do planejamento não informada!")
