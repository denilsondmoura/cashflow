from typing import Optional
from datetime import date
from cash_flow.application.ports.inbound.use_cases import PlanningUseCase
from cash_flow.application.ports.outbound.repositories.planning_repository import PlanningRepository
from cash_flow.application.ports.outbound.repositories.budget_repository import BudgetRepository
from cash_flow.application.ports.outbound.repositories.transaction_repository import TransactionRepository

from cash_flow.application.ports.inbound.commands.planning_commands import (
    CreatePlanningCommand,
    UpdatePlanningCommand
)
from cash_flow.application.ports.inbound.commands.budget_commands import (
    CreateBudgetPlanningCommand,
    UpdateBudgetPlanningCommand
)
from cash_flow.application.ports.inbound.commands.transaction_commands import (
    CreateRecurringTransactionPlanningCommand,
    UpdateTransactionPlanningCommand,
    FilterTransactionPlanningCommand
)

from cash_flow.domain.entities import Planning, Budget, Transaction
from cash_flow.domain.objects_values import Currency


class PlanningService(PlanningUseCase):
    def __init__(
        self, 
        planning_repo: PlanningRepository,
        budget_repo: BudgetRepository,
        transaction_repo: TransactionRepository
    ):
        self.planning_repo = planning_repo
        self.budget_repo = budget_repo
        self.transaction_repo = transaction_repo

    def create_planning(self, command: CreatePlanningCommand) -> Planning:
        planning = Planning(
            id=0,  # Repo will assign ID
            name=command.name,
            color=command.color,
            end_date=command.end_date,
            average_daily_expenditure=Currency(0),
            total_budgeted_amount=Currency(0),
            total_balance_amount=Currency(0),
            budgets=[],
            transactions=[],
            notifications=[]
        )
        return self.planning_repo.save(planning)

    def update_planning(self, command: UpdatePlanningCommand) -> Planning:
        planning = self.planning_repo.find_by_id(command.id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")
        
        planning.name = command.name
        planning.color = command.color
        planning.end_date = command.end_date
        
        return self.planning_repo.save(planning)

    def delete_planning(self, id: int) -> bool:
        return self.planning_repo.delete(id)

    def list_plannings(self) -> Optional[list[Planning]]:
        return self.planning_repo.list_all(page=1, page_size=100)

    def add_budget_to_planning(self, command: CreateBudgetPlanningCommand) -> bool:
        planning = self.planning_repo.find_by_id(command.planning_id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")
        
        budget = Budget(
            id=0,
            current_balance=command.current_balance,
            limit_amount=command.limit_amount,
            description=command.description,
            planning_id=command.planning_id
        )
        
        saved_budget = self.budget_repo.save(budget)
        planning.add_budget(saved_budget)
        self.planning_repo.save(planning)
        return True

    def update_budget_in_planning(self, command: UpdateBudgetPlanningCommand) -> bool:
        budget = self.budget_repo.find_by_id(command.id)
        if not budget:
            raise ValueError("Orçamento não encontrado!")
        
        planning = self.planning_repo.find_by_id(budget.planning_id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")
        
        budget.current_balance = command.current_balance
        budget.limit_amount = command.limit_amount
        budget.description = command.description
        
        self.budget_repo.save(budget)
        planning.update_budget(budget)
        self.planning_repo.save(planning)
        return True

    def remove_budget_from_planning(self, id: int) -> bool:
        budget = self.budget_repo.find_by_id(id)
        if not budget:
            raise ValueError("Orçamento não encontrado!")
        
        planning = self.planning_repo.find_by_id(budget.planning_id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")
        
        planning.remove_budget(budget)
        self.budget_repo.delete(id)
        self.planning_repo.save(planning)
        return True

    def list_budgets(self) -> Optional[list[Budget]]:
        return self.budget_repo.list_all(page=1, page_size=100)

    def add_recurring_transaction_to_planning(self, command: CreateRecurringTransactionPlanningCommand) -> bool:
        planning = self.planning_repo.find_by_id(command.planning_id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")
        
        # Temporary transaction to use logic in entity
        base_transaction = Transaction(
            id=0,
            due_date=command.due_date,
            description=command.description,
            amount=command.amount,
            type="outflow" if command.amount < 0 else "inflow",
            cleared=command.cleared,
            cleared_at=date.today() if command.cleared else None,
            auto_pay=command.auto_pay,
            planning_id=command.planning_id
        )
        
        if command.repeat:
            planning.add_recurring_transaction(
                base_transaction, 
                iterations=command.iterations, 
                repeat_until=command.repeat_until
            )
        else:
            planning.transactions.append(base_transaction)
            
        # Save all transactions
        for t in planning.transactions:
            if t.id == 0:
                self.transaction_repo.save(t)
        
        self.planning_repo.save(planning)
        return True

    def update_transaction_in_planning(self, command: UpdateTransactionPlanningCommand) -> bool:
        transaction = self.transaction_repo.find_by_id(command.id)
        if not transaction:
            raise ValueError("Transação não encontrada!")
            
        planning = self.planning_repo.find_by_id(transaction.planning_id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")
            
        transaction.due_date = command.due_date
        transaction.description = command.description
        transaction.amount = command.amount
        transaction.cleared = command.cleared
        transaction.cleared_at = command.cleared_at
        transaction.auto_pay = command.auto_pay
        
        self.transaction_repo.save(transaction)
        planning.update_transaction(transaction)
        self.planning_repo.save(planning)
        return True

    def remove_transaction_from_planning(self, id: int) -> bool:
        return self.transaction_repo.delete(id)

    def filter_transactions_in_planning(self, command: FilterTransactionPlanningCommand) -> Optional[list[Transaction]]:
        return self.transaction_repo.filter(
            data_from=command.data_from,
            data_to=command.data_to,
            description=command.description,
            type=command.type,
            cleared=command.cleared,
            auto_pay=command.auto_pay
        )
