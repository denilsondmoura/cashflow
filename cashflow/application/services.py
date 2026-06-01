from cashflow.application.ports.inbound.commands import planning_commands
from cashflow.application.ports.inbound.dtos.planning_dto import PlanningItemDTO
from cashflow.application.ports.inbound.commands import budget_commands
import contextlib
from typing import Optional, List
from datetime import date
from collections import defaultdict

from cashflow.application.ports.inbound.use_cases import PlanningUseCase
from cashflow.application.ports.inbound.dtos.transaction_dto import TransactionItemDTO, TransactionsGroupedByMonthDTO
from cashflow.application.ports.inbound.dtos.planning_dto import PlanningForecastScreenDTO
from cashflow.application.ports.inbound.dtos.planning_dto import BudgetItemDTO
from cashflow.application.ports.outbound.repositories.planning_repository import PlanningRepository
from cashflow.application.ports.outbound.repositories.budget_repository import BudgetRepository
from cashflow.application.ports.outbound.repositories.transaction_repository import TransactionRepository

from cashflow.application.ports.inbound.commands.planning_commands import (
    CreatePlanningCommand,
    UpdatePlanningCommand
)
from cashflow.application.ports.inbound.commands.budget_commands import (
    CreateBudgetPlanningCommand,
    UpdateBudgetPlanningCommand
)
from cashflow.application.ports.inbound.commands.transaction_commands import (
    CreateRecurringTransactionPlanningCommand,
    UpdateTransactionPlanningCommand,
    FilterTransactionPlanningCommand
)

from cashflow.domain.entities import Planning, Budget, Transaction
from cashflow.domain.objects_values import Currency


class PlanningService(PlanningUseCase):
    def __init__(
        self, 
        planning_repo: PlanningRepository,
        budget_repo: BudgetRepository,
        transaction_repo: TransactionRepository,
    ):
        self.planning_repo = planning_repo
        self.budget_repo = budget_repo
        self.transaction_repo = transaction_repo

    def create_planning(self, command: CreatePlanningCommand) -> Planning:
        planning = Planning(
            id=0,  # Repo will assign ID
            name=command.name,
            end_date=command.end_date,
            average_daily_expenditure=Currency(0),
            total_budgeted_amount=Currency(0),
            total_balance_amount=Currency(0),
            budgets=[],
            transactions=[],
            notifications=[],
            start_billing_cycle=command.start_billing_cycle,
            created_by=command.created_by
        )
        return self.planning_repo.save(planning)

    def update_planning(self, command: UpdatePlanningCommand) -> Planning:
        planning = self.planning_repo.find_by_id(command.id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")
        
        planning.name = command.name
        planning.end_date = command.end_date
        planning.start_billing_cycle = command.start_billing_cycle
        planning.updated_by = command.updated_by
        
        return self.planning_repo.save(planning)

    def delete_planning(self, id: int) -> bool:
        return self.planning_repo.delete(id)

    def list_plannings(self, username: Optional[str] = None) -> Optional[list[Planning]]:
        return self.planning_repo.list_all(page=1, page_size=100, username=username)

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

    def visualize_forecast_transactions_in_planning(self, planning_id: int) -> PlanningForecastScreenDTO:
        def group_transactions_dto_by_month(transactions_by_month: dict) -> List[TransactionsGroupedByMonthDTO]:
            MONTH_NAMES = {
                1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO",
                7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
            }

            grouped_list: List[TransactionsGroupedByMonthDTO] = []
            for month_num, txs in sorted(transactions_by_month.items()):
                month_name = MONTH_NAMES.get(month_num, "OUTRO")
                txs_sorted = sorted(txs, key=lambda tx: tx.due_date)
                total = sum(tx.amount.value for tx in txs_sorted)

                transactions_items_dto = []
                for tx in txs_sorted:
                    amount_raw_value = abs(tx.amount.value) if tx.type == 'outflow' else tx.amount.value
                    transaction_dto = TransactionItemDTO(
                        id = tx.id,
                        due_date_str = tx.due_date.strftime("%d/%m"),
                        due_date_iso = tx.due_date.strftime("%Y-%m-%d"),
                        description = tx.description,
                        amount_formatted = f"R$ {tx.amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        amount_raw = f"{amount_raw_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        cleared = tx.cleared,
                        type = tx.type
                    )

                    transactions_items_dto.append(transaction_dto)

                transactions_grouped_by_month_dto = TransactionsGroupedByMonthDTO(
                    month=month_name,
                    total_formatted=f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    transactions=transactions_items_dto
                )

                grouped_list.append(transactions_grouped_by_month_dto)
            
            return grouped_list

        planning = self.planning_repo.find_by_id(planning_id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")

        planning_item_dto = PlanningItemDTO(
            id=planning.id,
            name=planning.name
        )

        inflows_by_month = defaultdict(list)
        outflows_by_month = defaultdict(list)


        transactions = planning.transactions if planning.transactions else []
        if transactions:
            for t in transactions:
                month_num = t.due_date.month
                if t.type == "inflow" or t.amount.value >= 0:
                    inflows_by_month[month_num].append(t)
                else:
                    outflows_by_month[month_num].append(t)

        inflows_grouped_list = group_transactions_dto_by_month(inflows_by_month)
        outflows_grouped_list = group_transactions_dto_by_month(outflows_by_month)
 
        budgets_list: List[BudgetItemDTO] = []
        total_budget = 0
        budgets = planning.budgets if planning.budgets else []
        if budgets:
            for b in budgets:
                total_budget += b.limit_amount.value
                budget_item_dto = BudgetItemDTO(
                    id=b.id,
                    description=b.description,
                    amount_formatted=f"R$ {b.limit_amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    amount_raw=f"{b.limit_amount.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                budgets_list.append(budget_item_dto)

        total_budget_formatted = f"R$ {total_budget:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        return PlanningForecastScreenDTO(
            planning = planning_item_dto,
            inflows = inflows_grouped_list,
            outflows = outflows_grouped_list,
            budgets = budgets_list,
            total_budget_formatted = total_budget_formatted
        )
