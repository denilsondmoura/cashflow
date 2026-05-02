from src.application.ports.in.use_cases import MovimentacaoUseCase
from src.application.ports.out.repositories import OrcamentoRepository, MovimentacaoRepository

from src.application.commands.movimentacao_comands import (
    CriarMovimentacaoCommand,
    AtualizarMovimentacaoCommand,
    FiltrarMovimentacaoCommand
)


class MovimentacaoServices(MovimentacaoUseCase):
    def __init__(self, orcamento_repo: OrcamentoRepository, movimentacao_repo: MovimentacaoRepository):
        self.orcamento_repo = orcamento_repo
        self.movimentacao_repo = movimentacao_repo

    def criar_movimentacao(self, command: CriarMovimentacaoCommand) -> list[Movimentacao]:
        movimentacoes_criadas = []

        if not command.repetir:
            movimentacao = Movimentacao(
                data_prevista=command.data_prevista,
                descricao=command.descricao,
                valor=command.valor,
                foi_concluida=command.foi_concluida,
                data_conclusao=command.data_conclusao,
                categoria=command.categoria,
                eh_debito_automatico=command.eh_debito_automatico
            )

            self.movimentacao_repo.save(movimentacao)
            movimentacoes_criadas.append(movimentacao)
            
            return movimentacoes_criadas

        if command.repetir_ate:
            while movimentacao.data_prevista <= command.repetir_ate:
                movimentacao = Movimentacao(
                    data_prevista=command.data_prevista,
                    descricao=command.descricao,
                    valor=command.valor,
                    foi_concluida=command.foi_concluida,
                    data_conclusao=command.data_conclusao,
                    categoria=command.categoria,
                    eh_debito_automatico=command.eh_debito_automatico
                )
                self.movimentacao_repo.save(movimentacao)
                movimentacoes_criadas.append(movimentacao)

                movimentacao.data_prevista += timedelta(months=1)

        else:
            for i in range(command.qtd_repeticoes):
                movimentacao = Movimentacao(
                    data_prevista=command.data_prevista,
                    descricao= f"{command.descricao} ({i+1}/{command.qtd_repeticoes})",
                    valor=command.valor,
                    foi_concluida=command.foi_concluida,
                    data_conclusao=command.data_conclusao,
                    categoria=command.categoria,
                    eh_debito_automatico=command.eh_debito_automatico
                )
                self.movimentacao_repo.save(movimentacao)
                movimentacoes_criadas.append(movimentacao)

                movimentacao.data_prevista += timedelta(months=1)
            
        return movimentacoes_criadas

    def atualizar_movimentacao(self, command: AtualizarMovimentacaoCommand) -> Movimentacao:
        movimentacao = self.movimentacao_repo.find_by_id(command.id)

        if movimentacao is None:
            raise ValueError("Movimentação não encontrada")

        movimentacao = Movimentacao(
            id=movimentacao.id,
            data_prevista=command.data_prevista,
            descricao=command.descricao,
            valor=command.valor,
            foi_concluida=command.foi_concluida,
            data_conclusao=command.data_conclusao,
            categoria=command.categoria,
            eh_debito_automatico=command.eh_debito_automatico
        )

        self.movimentacao_repo.save(movimentacao)

    def deletar_movimentacao(self, id: int) -> bool:
        movimentacao = self.movimentacao_repo.find_by_id(id)

        if movimentacao is None:
            raise ValueError("Movimentação não encontrada")

        return self.movimentacao_repo.delete(movimentacao.id)


    def listar_movimentacoes(self) -> Optional[list[Movimentacao]]:
        return self.movimentacao_repo.find_all()

    def filtrar_movimentacoes(self, command: FiltrarMovimentacaoCommand) -> Optional[list[Movimentacao]]:
        return self.movimentacao_repo.filter(
            descricao=command.descricao,
            data_prevista_inicio=command.data_prevista_inicio,
            data_prevista_fim=command.data_prevista_fim,
            categoria_id=command.categoria_id,
            foi_concluida=command.foi_concluida
        )