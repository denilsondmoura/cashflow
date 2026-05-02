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

from commands.categoria_commands import (
    CriarCategoriaCommand,
    AtualizarCategoriaCommand
)

from commands.orcamento_commands import (
    CriarOrcamentoCommand,
    AtualizarOrcamentoCommand
)

from commands.planejamento_commands import (
    CriarPlanejamentoCommand,
    AtualizarPlanejamentoCommand
)

class MovimentacaoUseCase(ABC):
    @abstractmethod
    def criar_movimentacao(self, command: CriarMovimentacaoCommand) -> list[Movimentacao]:
        pass

    @abstractmethod
    def atualizar_movimentacao(self, command: AtualizarMovimentacaoCommand) -> Movimentacao:
        pass

    @abstractmethod
    def deletar_movimentacao(self, id: int) -> bool:
        pass

    @abstractmethod
    def listar_movimentacoes(self) -> list[Movimentacao]:
        pass

    @abstractmethod
    def filtrar_movimentacoes(self, command: FiltrarMovimentacaoCommand) -> list[Movimentacao]:
        pass
        

class OrcamentoUseCase(ABC):
    @abstractmethod
    def criar_orcamento(self, command: CriarOrcamentoCommand) -> Orcamento:
        pass

    @abstractmethod
    def atualizar_orcamento(self, command: AtualizarOrcamentoCommand) -> Orcamento:
        pass

    @abstractmethod
    def deletar_orcamento(self, id: int) -> bool:
        pass

    @abstractmethod
    def listar_orcamentos(self) -> list[Orcamento]:
        pass


class CategoriaUseCase(ABC):
    @abstractmethod
    def criar_categoria(self, command: CriarCategoriaCommand) -> Categoria:
        pass

    @abstractmethod
    def atualizar_categoria(self, command: AtualizarCategoriaCommand) -> Categoria:
        pass

    @abstractmethod
    def deletar_categoria(self, id: int) -> bool:
        pass

    @abstractmethod
    def listar_categorias(self) -> list[Categoria]:
        pass

    
class PlanejamentoUseCase(ABC):
    @abstractmethod
    def criar_planejamento(self, command: CriarPlanejamentoCommand) -> Planejamento:
        pass

    @abstractmethod
    def atualizar_planejamento(self, command: AtualizarPlanejamentoCommand) -> Planejamento:
        pass

    @abstractmethod
    def deletar_planejamento(self, id: int) -> bool:
        pass

    @abstractmethod
    def listar_planejamentos(self) -> list[Planejamento]:
        pass
