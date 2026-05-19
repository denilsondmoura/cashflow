from abc import ABC, abstractmethod
from typing import List
from cashflow.domain.entities import Transaction

class TransactionGroupPresenter(ABC):
    @abstractmethod
    def group_transactions(self, transactions: List[Transaction]) -> dict:
        pass
