from abc import ABC, abstractmethod

from src.domain.entities import (
    Categoria, 
    Movimentacao, 
    Orcamento, 
    Planejamento
)

from commands.movimentacao_comands import (
    CriarMovimentacaoCommand,
    AtualizarMovimentacaoCommand,
    FiltrarMovimentacaoCommand
)


class MovimentacaoUseCase(ABC):
    @abstractmethod
    def criar_movimentacao(self, command: CriarMovimentacaoCommand):
        pass

    @abstractmethod
    def atualizar_movimentacao(self, command: AtualizarMovimentacaoCommand):
        pass

    @abstractmethod
    def deletar_movimentacao(self, id: int):
        pass

    @abstractmethod
    def listar_movimentacoes(self):
        pass

    @abstractmethod
    def filtrar_movimentacoes(self, command: FiltrarMovimentacaoCommand):
        pass
        

class OrcamentoUseCase(ABC):
    @abstractmethod
    def criar_orcamento(self, orcamento: Orcamento):
        pass

    @abstractmethod
    def atualizar_orcamento(self, orcamento: Orcamento):
        pass

    @abstractmethod
    def deletar_orcamento(self, orcamento: Orcamento):
        pass

    @abstractmethod
    def listar_orcamentos(self):
        pass


class CategoriaUseCase(ABC):
    @abstractmethod
    def criar_categoria(self, categoria: Categoria):
        pass

    @abstractmethod
    def atualizar_categoria(self, categoria: Categoria):
        pass

    @abstractmethod
    def deletar_categoria(self, categoria: Categoria):
        pass

    @abstractmethod
    def listar_categorias(self):
        pass

    
class PlanejamentoUseCase(ABC):
    @abstractmethod
    def criar_planejamento(self, planejamento: Planejamento):
        pass

    @abstractmethod
    def atualizar_planejamento(self, planejamento: Planejamento):
        pass

    @abstractmethod
    def deletar_planejamento(self, planejamento: Planejamento):
        pass

    @abstractmethod
    def listar_planejamentos(self):
        pass
