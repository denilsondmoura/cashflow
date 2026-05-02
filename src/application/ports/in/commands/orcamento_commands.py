from src.domain.entities import Categoria
from src.domain.objects_values import Currency
from dataclasses import dataclass


@dataclass
class CriarOrcamentoCommand:
    saldo_atual: Currency
    saldo_previsto: Currency
    categoria: Categoria


@dataclass
class AtualizarOrcamentoCommand:
    id: int
    saldo_atual: Currency
    saldo_previsto: Currency
    categoria: Categoria

