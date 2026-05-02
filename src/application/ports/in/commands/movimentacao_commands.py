from src.domain.entities import Categoria, Movimentacao, Orcamento, Planejamento
from src.domain.objects_values import Currency
from datetime import date
from dataclasses import dataclass

@dataclass
class CriarMovimentacaoCommand:
    data_prevista: date
    descricao: str
    valor: Currency
    foi_concluida: bool
    data_conclusao: date
    categoria: Categoria
    eh_debito_automatico: bool
    repetir: bool
    qtd_repeticoes: int
    repetir_ate: date

    def __post_init__(self):
        current_date = date.today()
        if self.data_prevista < current_date:
            raise ValueError("Data prevista menor que a data atual")

        if self.data_conclusao < current_date:
            raise ValueError("Data de conclusão menor que a data atual")

        if self.repetir_ate < self.data_prevista:
            raise ValueError("Data de repetição menor que a data prevista")

        if self.qtd_repeticoes < 1:
            raise ValueError("Quantidade de repetições menor que 1")

        if self.repetir and self.repetir_ate is None:
            raise ValueError("Data de repetição obrigatória")

        if self.foi_concluida and self.data_conclusao is None:
            raise ValueError("Data de conclusão obrigatória")


@dataclass
class AtualizarMovimentacaoCommand:
    id: int
    data_prevista: date
    descricao: str
    valor: Currency
    foi_concluida: bool
    data_conclusao: date
    categoria: Categoria
    eh_debito_automatico: bool
    repetir: bool
    qtd_repeticoes: int
    repetir_ate: date


@dataclass
class AtualizarMovimentacaoCommand:
    id: int
    data_prevista: date
    descricao: str
    valor: Currency
    foi_concluida: bool
    data_conclusao: date
    categoria: Categoria
    eh_debito_automatico: bool
    repetir: bool
    qtd_repeticoes: int
    repetir_ate: date
    alertas: list[AlertaMovimentacao]


@dataclass
class FiltrarMovimentacaoCommand:
    data_prevista_inicio: date
    data_prevista_fim: date
    descricao: str
    categoria: Categoria
    alertas: list[AlertaMovimentacao]


@dataclass
class FiltrarMovimentacaoCommand:
    id: int
    data_prevista: date
    descricao: str
    valor: Currency
    foi_concluida: bool
    data_conclusao: date
    categoria: Categoria
    eh_debito_automatico: bool
    repetir: bool
    qtd_repeticoes: int
    repetir_ate: date
    alertas: list[AlertaMovimentacao]


@dataclass
class ExcluirMovimentacaoCommand:
    id: int
    data_prevista: date
    descricao: str
    valor: Currency
    foi_concluida: bool
    data_conclusao: date
    categoria: Categoria
    eh_debito_automatico: bool
    repetir: bool
    qtd_repeticoes: int
    repetir_ate: date
    alertas: list[AlertaMovimentacao]


@dataclass
class FiltrarMovimentacaoCommand:
    data_prevista_inicio: date
    data_prevista_fim: date
    descricao: str
    categoria: Categoria