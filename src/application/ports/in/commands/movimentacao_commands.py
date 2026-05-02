from src.domain.entities import Categoria
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
        if not self.data_prevista:
            raise ValueError("Data prevista não informada")
        
        if not self.descricao:
            raise ValueError("Descrição não informada")

        if not self.valor:
            raise ValueError("Valor não informado")

        if self.repetir and (not self.qtd_repeticoes and not self.repetir_ate):
            raise ValueError("Quantidade de repetições ou data de repetição devem ser informados")  


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