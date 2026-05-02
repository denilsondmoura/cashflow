from abc import ABC, abstractmethod
from src.domain.entities import Orcamento
from typing import Optional

class OrcamentoRepository(ABC):
    @abstractmethod
    def save(self, orcamento: Orcamento) -> Orcamento:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Orcamento]:
        pass

    @abstractmethod
    def filter(
        self,
        categoria_id: Optional[int] = None,
    ) -> list[Orcamento]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass