from src.application.ports.in.use_cases import PlanejamentoUseCase
from src.application.ports.out.repositories import PlanejamentoRepository

from src.application.commands.planejamento_commands import (
    CriarPlanejamentoCommand,
    AtualizarPlanejamentoCommand
)

from src.domain.entities import Planejamento


class PlanejamentoService(PlanejamentoUseCase):
    def __init__(self, planejamento_repo: PlanejamentoRepository):
        self.planejamento_repo = planejamento_repo

    def criar_planejamento(self, command: CriarPlanejamentoCommand) -> Planejamento:
        planejamento = Planejamento(
            planejar_ate=command.planejar_ate
        )
        return self.planejamento_repo.save(planejamento)

    def atualizar_planejamento(self, command: AtualizarPlanejamentoCommand) -> Planejamento:
        planejamento = self.planejamento_repo.find_by_id(command.id)
        if planejamento is None:
            raise ValueError("Planejamento não encontrado")

        planejamento = Planejamento(
            id=planejamento.id,
            planejar_ate=command.planejar_ate
        )
        return self.planejamento_repo.save(planejamento)

    def deletar_planejamento(self, id: int) -> bool:
        planejamento = self.planejamento_repo.find_by_id(id)
        if planejamento is None:
            raise ValueError("Planejamento não encontrado")

        return self.planejamento_repo.delete(planejamento.id)

    def listar_planejamentos(self) -> list[Planejamento]:
        return self.planejamento_repo.find_all()
