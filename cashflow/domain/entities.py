from cashflow.domain.objects_values import Currency
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Optional
import calendar

@dataclass
class User:
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    plannings: list['Planning']


@dataclass
class Planning:
    id: int
    name: str
    end_date: date
    average_daily_expenditure: Currency
    total_budgeted_amount: Currency
    total_balance_amount: Currency
    budgets: list['Budget']
    transactions: list['Transaction']
    notifications: list['Notification']
    created_at: date
    updated_at: date
    created_by: User
    updated_by: User
    status: str = "updated"

    def __post_init__(self):
        if self.end_date < date.today():
            raise ValueError("Data final do planejamento deve ser maior que a data atual!") 

    def _add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def _update_values(self):
        self.updated_at = date.today()
        self.total_budgeted_amount = sum(budget.limit_amount for budget in self.budgets) if self.budgets else Currency(0)
        self.total_balance_amount = sum(budget.current_balance for budget in self.budgets) if self.budgets else Currency(0)
        if self.total_budgeted_amount:
            self.average_daily_expenditure = self.total_budgeted_amount / 30.5
        else:
            self.average_daily_expenditure = Currency(0)

    def add_recurring_transaction(self, transaction: 'Transaction', iterations=None, repeat_until=None):
        current_date = transaction.due_date
        count = 1
        
        while True:
            if current_date > self.end_date:
                self.end_date = current_date
            
            if repeat_until and current_date > repeat_until:
                break
            
            if iterations and count > iterations:   
                break

            final_desc = f"{transaction.description} ({count}/{iterations})" if iterations else transaction.description
            due_today = current_date <= date.today()
            transaction_cleared = transaction.cleared or (transaction.auto_pay and due_today)
            cleared_at = date.today() if transaction_cleared else None
            transaction_type = "inflow" if transaction.amount >= 0 else "outflow"

            new_transaction = Transaction(
                id=0,
                description=final_desc,
                amount=transaction.amount,
                due_date=current_date,
                cleared=transaction_cleared,
                cleared_at=cleared_at,
                auto_pay=transaction.auto_pay,
                type=transaction_type,
                planning_id=transaction.planning_id
            )
            self.transactions.append(new_transaction)
            self.updated_at = date.today()
            
            current_date = self._add_months(current_date, 1)
            count += 1

    def update_transaction(self, transaction: 'Transaction'):
        # TODO: Corrigir essa implementação, acho que não precisa de um for pra isso
        transaction_index = -1
        for i, t in enumerate(self.transactions):
            if t.id == transaction.id:
                transaction_index = i
                break
        
        if transaction_index == -1:
            raise ValueError("Transação não encontrada!")

        due_today = transaction.due_date <= date.today()
        transaction_cleared = transaction.cleared or (transaction.auto_pay and due_today)

        if transaction.cleared:
            cleared_at = transaction.cleared_at if transaction.cleared_at else date.today()
        else:
            cleared_at = None

        transaction_type = "inflow" if transaction.amount >= 0 else "outflow"

        self.transactions[transaction_index].description = transaction.description
        self.transactions[transaction_index].amount = transaction.amount
        self.transactions[transaction_index].due_date = transaction.due_date
        self.transactions[transaction_index].type = transaction_type
        self.transactions[transaction_index].cleared = transaction_cleared
        self.transactions[transaction_index].cleared_at = cleared_at
        self.transactions[transaction_index].auto_pay = transaction.auto_pay
        self.updated_at = date.today()
        return True

    def add_budget(self, budget: 'Budget'):
        self.budgets.append(budget)
        self._update_values()

        return True

    def update_budget(self, budget: 'Budget'):
        # TODO: Corrigir essa implementação, acho que não precisa de um for pra isso
        budget_index = -1
        for i, b in enumerate(self.budgets):
            if b.id == budget.id:
                budget_index = i
                break

        if budget_index == -1:
            raise ValueError("Orçamento não encontrado!")

        self.budgets[budget_index].current_balance = budget.current_balance
        self.budgets[budget_index].limit_amount = budget.limit_amount
        self.budgets[budget_index].description = budget.description

        self._update_values()

        return True
    
    def remove_budget(self, budget: 'Budget'):
        budget_index = -1
        for i, b in enumerate(self.budgets):
            if b.id == budget.id:
                budget_index = i
                break

        if budget_index == -1:
            raise ValueError("Orçamento não encontrado!")

        self.budgets.pop(budget_index)
        self._update_values()
        return True

    def verify_transactions_cleared(self):
        for transaction in self.transactions:
            if transaction.due_date <= date.today() and not transaction.cleared:
                if transaction.auto_pay:
                    transaction.cleared = True
                    transaction.cleared_at = date.today()

                else:
                    transaction.due_date = date.today()
                    self.notifications.append(
                        Notification(
                            id=0,
                            trigger_date=date.today(),
                            message=f"A transação '{transaction.description}: {transaction.amount.mask_value()}' já aconteceu?",
                            related_transaction_id=transaction.id,
                            is_read=False,
                            planning_id=transaction.planning_id
                        )
                    )
                self.updated_at = date.today()
                
        return True


@dataclass
class Budget:
    id: int
    current_balance: Currency
    limit_amount: Currency
    description: str
    planning_id: int
    created_at: date
    updated_at: date
    created_by: User
    updated_by: User

    def __post_init__(self):
        if not self.current_balance:
            self.current_balance = Currency(0)
        
        if not self.limit_amount:
            self.limit_amount = Currency(0)

        if not self.planning_id:
            raise ValueError("Planejamento ao qual o orçamento pertence não foi informado!")


@dataclass
class Transaction:
    id: int
    due_date: date
    description: str
    amount: Currency
    type: str
    cleared: bool
    cleared_at: date
    auto_pay: bool
    planning_id: int
    created_at: date
    updated_at: date
    created_by: User
    updated_by: User

    def __post_init__(self):
        if not self.amount:
            self.amount = Currency(0)
        
        if not self.cleared:
            self.cleared = False

        if not self.auto_pay:
            self.auto_pay = False
        
        if not self.type:
            self.type = "outflow" if self.amount < Currency(0) else "inflow"

        
        if not self.planning_id:
            raise ValueError("Planejamento ao qual a transação pertence não foi informado!")


@dataclass
class Notification:
    id: int
    trigger_date: date
    message: str
    related_transaction_id: int
    is_read: bool
    planning_id: int
    created_at: date
    updated_at: date
    created_by: User
    updated_by: User

    
