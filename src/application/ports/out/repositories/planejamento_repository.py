from abc import ABC, abstractmethod
from src.domain.entities import Planejamento
from typing import Optional

class PlanejamentoRepository(ABC):
    @abstractmethod
    def save(self, planejamento: Planejamento) -> Planejamento:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Planejamento]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass