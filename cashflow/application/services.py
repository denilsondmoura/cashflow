import contextlib
import calendar
import math
from typing import Optional, List
from datetime import date, datetime
from collections import defaultdict
from decimal import Decimal

from cashflow.application.ports.inbound.commands import planning_commands
from cashflow.application.ports.inbound.dtos.planning_dto import PlanningItemDTO
from cashflow.application.ports.inbound.commands import budget_commands
from cashflow.application.ports.inbound.use_cases import PlanningUseCase
from cashflow.application.ports.inbound.dtos.transaction_dto import TransactionItemDTO, TransactionsGroupedByMonthDTO
from cashflow.application.ports.inbound.dtos.planning_dto import PlanningForecastScreenDTO,PlanningCashflowScreenDTO
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
    CreateRecurringTransactionToPlanningCommand,
    UpdateTransactionPlanningCommand
)

from cashflow.domain.entities import Planning, Budget, Transaction
from cashflow.domain.enums import MONTH_NAMES


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
            average_daily_expenditure=Decimal(0),
            total_budgeted_amount=Decimal(0),
            total_balance_amount=Decimal(0),
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

    def add_recurring_transaction_to_planning(self, command: CreateRecurringTransactionToPlanningCommand) -> bool:
        planning = self.planning_repo.find_by_id(command.planning_id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")
        
        # Temporary transaction to use logic in entity
        base_transaction = Transaction(
            id=0,
            due_date=command.due_date,
            description=command.description,
            amount=command.amount,
            type=command.type,
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
        
        cleared_at = transaction.cleared_at if command.cleared else None
        if not transaction.cleared and command.cleared:
            cleared_at = date.today()

        transaction.due_date = command.due_date
        transaction.description = command.description
        transaction.amount = command.amount
        transaction.cleared = command.cleared
        transaction.cleared_at = cleared_at
        
        self.transaction_repo.save(transaction)
        planning.update_transaction(transaction)
        self.planning_repo.save(planning)
        return True

    def remove_transaction_from_planning(self, id: int) -> bool:
        return self.transaction_repo.delete(id)

    def visualize_forecast_transactions_in_planning(self, planning_id: int) -> PlanningForecastScreenDTO:
        def group_transactions_dto_by_month(transactions_by_month: dict) -> List[TransactionsGroupedByMonthDTO]:

            grouped_list: List[TransactionsGroupedByMonthDTO] = []
            for month_num, txs in sorted(transactions_by_month.items()):
                month_name = MONTH_NAMES.get(month_num, "OUTRO")
                txs_sorted = sorted(txs, key=lambda tx: tx.due_date)
                total = sum(tx.amount for tx in txs_sorted)

                transactions_items_dto = []
                for tx in txs_sorted:
                    amount_raw_value = abs(tx.amount) if tx.type == 'outflow' else tx.amount
                    transaction_dto = TransactionItemDTO(
                        id = tx.id,
                        due_date_str = tx.due_date.strftime("%d/%m"),
                        due_date_iso = tx.due_date.strftime("%Y-%m-%d"),
                        description = tx.description,
                        amount_formatted = f"R$ {tx.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
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
                if t.type == "inflow" or t.amount >= 0:
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
                total_budget += b.limit_amount
                budget_item_dto = BudgetItemDTO(
                    id=b.id,
                    description=b.description,
                    amount_formatted=f"R$ {b.limit_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    amount_raw=f"{b.limit_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
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

    def visualise_cashflow_in_planning(self, planning_id: int) -> PlanningCashflowScreenDTO:
        def to_date(dt):
            if isinstance(dt, datetime):
                return dt.date()
            return dt

        def format_currency(val):
            prefix = "-" if val < 0 else ""
            abs_val = abs(val)
            return f"{prefix}R$ {abs_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        planning = self.planning_repo.find_by_id(planning_id)
        if not planning:
            raise ValueError("Planejamento não encontrado!")

        planning_item_dto = PlanningItemDTO(
            id=planning.id,
            name=planning.name
        )
            
        transactions = planning.transactions if planning.transactions else []
        
        start_date = to_date(planning.created_at) if planning.created_at else date.today()
        end_date = to_date(planning.end_date) if planning.end_date else date.today()
        
        planning_months = []
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            planning_months.append((current_date.year, current_date.month))
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        for transaction in transactions:
            due_date = to_date(transaction.due_date)
            mouth = (due_date.year, due_date.month)
            if mouth not in planning_months:
                planning_months.append(mouth)
                
        planning_months = sorted(list(set(planning_months)))
        
        total_balance = sum(b.current_balance for b in planning.budgets) if planning.budgets else Decimal('0.00')
        
        current_baseline = total_balance
        current_saldo = total_balance
        
        diario_val = planning.average_daily_expenditure if planning.average_daily_expenditure else Decimal('0.00')
            
        months_data = []
        for year, month in planning_months:
            month_name = MONTH_NAMES.get(month, "OUTRO")
            _, num_days = calendar.monthrange(year, month)
            
            days_data = []
            for day in range(1, num_days + 1):
                day_date = date(year, month, day)
                
                day_inflows_txs = [t for t in transactions if to_date(t.due_date) == day_date and (t.type == "inflow" or t.amount >= 0)]
                day_inflow_sum = sum(t.amount for t in day_inflows_txs)
                
                day_outflows_txs = [t for t in transactions if to_date(t.due_date) == day_date and not (t.type == "inflow" or t.amount >= 0)]
                day_outflow_sum = sum(abs(t.amount) for t in day_outflows_txs)
                
                day_outflow_realized_sum = sum(abs(t.amount) for t in day_outflows_txs if t.cleared or t.auto_pay)
                
                current_baseline = current_baseline + day_inflow_sum - day_outflow_sum - diario_val
                current_saldo = current_saldo + day_inflow_sum - day_outflow_realized_sum - diario_val
                
                days_data.append({
                    "date_str": f"{day:02d}/{month:02d}",
                    "inflow_formatted": format_currency(day_inflow_sum) if day_inflow_sum > 0 else "-",
                    "outflow_formatted": format_currency(day_outflow_sum) if day_outflow_sum > 0 else "-",
                    "diario_formatted": format_currency(diario_val),
                    "saldo_formatted": format_currency(current_saldo),
                    "baseline_formatted": format_currency(current_baseline),
                })
                
            alerts = []
            if current_saldo < 0:
                alerts.append({
                    "type": "danger",
                    "message": f"Parece que nesse mês você vai terminar {format_currency(current_saldo)} no negativo, não seria a hora ideal para revisar seus gastos ou quem sabe buscar uma venda extra?"
                })
            else:
                alerts.append({
                    "type": "success",
                    "message": f"Parece que nesse mês vai sobrar {format_currency(current_saldo)}, que tal colocar na sua reserva de emergencia ou em algum item da sua lista de desejos?"
                })
                
            if current_saldo < current_baseline:
                diff = current_baseline - current_saldo
                days_to_recover = math.ceil(diff / diario_val) if diario_val > 0 else 0
                alerts.append({
                    "type": "warning",
                    "message": f"Seu saldo esta {format_currency(diff)} abaixo do planejado, mas nada que maneirar nos gastos por {days_to_recover} dias não resolva ;)"
                })
                
            months_data.append({
                "month_name": f"{month_name}",
                "days": days_data,
                "alerts": alerts
            })
            
        budget_list: List[BudgetItemDTO] = []
        if planning.budgets:
            for b in planning.budgets:
                budget_item_dto = BudgetItemDTO(
                    id=b.id,
                    description=b.description,
                    amount_formatted=f"R$ {b.limit_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    amount_raw=f"{b.limit_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                budget_list.append(budget_item_dto)

        return PlanningCashflowScreenDTO(
            planning=planning_item_dto,
            months_data=months_data,
            budgets=budget_list,
            total_balance_formatted=format_currency(total_balance),
            diario_val_formatted=format_currency(diario_val)
        )
