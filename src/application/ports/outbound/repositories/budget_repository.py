from abc import ABC, abstractmethod
from src.domain.entities import Budget
from typing import Optional

class BudgetRepository(ABC):
    @abstractmethod
    def save(self, budget: Budget) -> Budget:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Budget]:
        pass

    @abstractmethod
    def list_all(self, page: int, page_size: int) -> Optional[list[Budget]]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass