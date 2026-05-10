from objects_values import Currency
from datetime import date
from dataclasses import dataclass

@dataclass
class Planning:
    id: int
    end_date: date
    average_daily_expenditure: Currency
    total_budgeted_amount: Currency
    total_balance_amount: Currency
    budgets: list[Budget]
    transactions: list[Transaction]
    notifications: list[Notification]

    def _update_values(self):
        self.total_budgeted_amount = sum([budget.limit_amount for budget in self.budgets])
        self.total_balance_amount = sum([budget.current_balance for budget in self.budgets])
        self.average_daily_expenditure = self.total_budgeted_amount / 30.5

    def add_recurring_transaction(self, transaction: Transaction, iterations=None, repeat_until=None):
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

            transaction = Transaction(
                description=final_desc,
                amount=transaction.amount,
                due_date=current_date,
                type=transaction_type,
                cleared=transaction_cleared,
                cleared_at=cleared_at,
                auto_pay=transaction.auto_pay
            )
            self.transactions.append(transaction)
            
            current_date = current_date + relativedelta(months=1)
            count += 1

    def update_transaction(self, transaction: Transaction):
        transaction_index = self.transactions.index(transaction)

        if transaction_index == -1:
            raise ValueError("Transação não encontrada!")

        due_today = transaction.due_date <= date.today()
        transaction_cleared = transaction.cleared or (transaction.auto_pay and due_today)
        cleared_at = date.today() if transaction_cleared else None
        transaction_type = "inflow" if transaction.amount >= 0 else "outflow"

        self.transactions[transaction_index].description = transaction.description
        self.transactions[transaction_index].amount = transaction.amount
        self.transactions[transaction_index].due_date = transaction.due_date
        self.transactions[transaction_index].type = transaction_type
        self.transactions[transaction_index].cleared = transaction_cleared
        self.transactions[transaction_index].cleared_at = cleared_at
        self.transactions[transaction_index].auto_pay = transaction.auto_pay
        return True

    def add_budget(self, budget: Budget):
        self.budgets.append(budget)
        self._update_values()

        return True

    def update_budget(self, budget: Budget):
        budget_index = self.budgets.index(budget)

        if budget_index == -1:
            raise ValueError("Orçamento não encontrado!")

        self.budgets[budget_index].current_balance = budget.current_balance
        self.budgets[budget_index].limit_amount = budget.limit_amount
        self.budgets[budget_index].description = budget.description

        self._update_values()

        return True
    
    def remove_budget(self, budget: Budget):
        budget_index = self.budgets.index(budget)

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
                            trigger_date=date.today(),
                            message=f"A transação '{transaction.description}: {transaction.amount.mask_value()}' já aconteceu?",
                            related_transaction_id=transaction.id,
                            is_read=False
                        )
                    )
                return False
        return True


@dataclass
class Budget:
    id: int
    current_balance: Currency
    limit_amount: Currency
    description: str


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


@dataclass
class Notification:
    id: int
    trigger_date: date
    message: str
    related_transaction_id: int
    is_read: bool
