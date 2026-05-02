from src.application.ports.in.use_cases import OrcamentoUseCase
from src.application.ports.out.repositories import OrcamentoRepository
from src.domain.entities import Orcamento


from src.application.commands.orcamento_commands import (
    CriarOrcamentoCommand,
    AtualizarOrcamentoCommand
)


class OrcamentoService(OrcamentoUseCase):
    def __init__(self, orcamento_repo: OrcamentoRepository):
        self.orcamento_repo = orcamento_repo

    def criar_orcamento(self, command: CriarOrcamentoCommand) -> Orcamento:
        orcamento = Orcamento(
            categoria=command.categoria,
            valor_diaria=command.valor_diaria,
            total_orcado=command.total_orcado,
            orcamentos=command.orcamentos,
            movimentacoes=command.movimentacoes
        )
        return self.orcamento_repo.save(orcamento)

    def atualizar_orcamento(self, command: AtualizarOrcamentoCommand) -> Orcamento:
        orcamento = self.orcamento_repo.find_by_id(command.id)
        if orcamento is None:
            raise ValueError("Orcamento não encontrado")

        orcamento = Orcamento(
            id=orcamento.id,
            categoria=command.categoria,
            valor_diaria=command.valor_diaria,
            total_orcado=command.total_orcado,
            orcamentos=command.orcamentos,
            movimentacoes=command.movimentacoes
        )
        return self.orcamento_repo.save(orcamento)

    def deletar_orcamento(self, id: int) -> bool:
        orcamento = self.orcamento_repo.find_by_id(id)
        if orcamento is None:
            raise ValueError("Orcamento não encontrado")

        return self.orcamento_repo.delete(orcamento.id)

    def listar_orcamentos(self) -> list[Orcamento]:
        return self.orcamento_repo.find_all()  