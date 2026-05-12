from abc import ABC, abstractmethod
from typing import Optional

from cashflow.domain.entities import (
    Planning, 
    Budget, 
    Transaction
)

from .commands.planning_commands import (
    CreatePlanningCommand,
    UpdatePlanningCommand
)

from .commands.budget_commands import (
    CreateBudgetPlanningCommand,
    UpdateBudgetPlanningCommand
)

from .commands.transaction_commands import (
    CreateRecurringTransactionPlanningCommand,
    UpdateTransactionPlanningCommand,
    FilterTransactionPlanningCommand
)


class PlanningUseCase(ABC):
    @abstractmethod
    def create_planning(self, command: CreatePlanningCommand) -> Planning:
        pass

    @abstractmethod
    def update_planning(self, command: UpdatePlanningCommand) -> Planning:
        pass

    @abstractmethod
    def delete_planning(self, id: int) -> bool:
        pass

    @abstractmethod
    def list_plannings(self) -> Optional[list[Planning]]:
        pass

    @abstractmethod
    def add_budget_to_planning(self, command: CreateBudgetPlanningCommand) -> bool:
        pass

    @abstractmethod
    def update_budget_in_planning(self, command: UpdateBudgetPlanningCommand) -> bool:
        pass

    @abstractmethod
    def remove_budget_from_planning(self, id: int) -> bool:
        pass

    @abstractmethod
    def list_budgets(self) -> Optional[list[Budget]]:
        pass

    @abstractmethod
    def add_recurring_transaction_to_planning(self, command: CreateRecurringTransactionPlanningCommand) -> bool:
        pass

    @abstractmethod
    def update_transaction_in_planning(self, command: UpdateTransactionPlanningCommand) -> bool:
        pass

    @abstractmethod
    def remove_transaction_from_planning(self, id: int) -> bool:
        pass
    
    @abstractmethod
    def filter_transactions_in_planning(self, command: FilterTransactionPlanningCommand) -> Optional[list[Transaction]]:
        pass
