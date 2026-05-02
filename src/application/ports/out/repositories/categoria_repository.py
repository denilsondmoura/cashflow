from abc import ABC, abstractmethod
from src.domain.entities import Categoria
from typing import Optional


class CategoriaRepository(ABC):
    @abstractmethod
    def save(self, categoria: Categoria) -> Categoria:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Categoria]:
        pass

    @abstractmethod
    def filter(
        self,
        descricao: Optional[str] = None,
    ) -> list[Categoria]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
