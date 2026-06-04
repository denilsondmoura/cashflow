from datetime import date
from pydantic import BaseModel, Field

class CreatePlanningCommand(BaseModel):
    name: str = Field(min_length=2)
    end_date: date
    start_billing_cycle: int
    created_by: str


class UpdatePlanningCommand(BaseModel):
    id: int
    name: str =Field(min_length=2)
    end_date: date
    start_billing_cycle: int
    updated_by: str
