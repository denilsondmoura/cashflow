from abc import ABC, abstractmethod
from cashflow.domain.entities import Transaction
from typing import Optional
from datetime import date

class TransactionRepository(ABC):
    @abstractmethod
    def save(self, transaction: Transaction) -> Transaction:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Transaction]:
        pass

    @abstractmethod
    def list_all(self, page: int, page_size: int) -> Optional[list[Transaction]]:
        pass

    @abstractmethod
    def filter(
        self,
        data_from: Optional[date] = None,
        data_to: Optional[date] = None,
        description: Optional[str] = None,
        type: Optional[str] = None,
        cleared: Optional[bool] = None,
        auto_pay: Optional[bool] = None
    ) -> Optional[Transaction]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass