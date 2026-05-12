from abc import ABC, abstractmethod
from cashflow.domain.entities import Planning
from typing import Optional

class PlanningRepository(ABC):
    @abstractmethod
    def save(self, planning: Planning) -> Planning:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Planning]:
        pass
    
    @abstractmethod
    def list_all(self, page: int, page_size: int) -> Optional[list[Planning]]:
        pass

    @abstractmethod 
    def delete(self, id: int) -> bool:
        pass