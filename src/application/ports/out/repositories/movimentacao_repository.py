from abc import ABC, abstractmethod
from src.domain.entities import Movimentacao
from typing import Optional
from datetime import date

class MovimentacaoRepository(ABC):
    @abstractmethod
    def save(self, movimentacao: Movimentacao) -> Movimentacao:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Movimentacao]:
        pass

    @abstractmethod
    def find_all(self) -> Optional[Movimentacao]:
        pass

    @abstractmethod
    def filter(
        self,
        descricao: Optional[str] = None,
        data_prevista_inicio: Optional[date] = None,
        data_prevista_fim: Optional[date] = None,
        categoria_id: Optional[int] = None,
        foi_concluida: Optional[bool] = None
    ) -> Optional[Movimentacao]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass