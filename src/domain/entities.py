from objects_values import Currency
from datetime import date
from dataclasses import dataclass

@dataclass
class Planejamento:
    planejar_ate: date
    valor_diaria: Currency
    total_orcado: Currency
    orcamentos: list[Orcamento]
    movimentacoes: list[Movimentacao]

@dataclass
class Orcamento:
    saldo_atual: Currency
    saldo_previsto: Currency
    categoria: Categoria

@dataclass
class Movimentacao:
    data_prevista: date
    descricao: str
    valor: Currency
    foi_concluida: bool
    data_conclusao: date
    categoria: Categoria
    eh_debito_automatico: bool
    alertas: list[AlertaMovimentacao]

    # Sempre que uma movimentação for criada verificar se a meta_mensal da categoria não foi batida. Se foi, gerar alerta
    # Se chegar a data_prevista e ainda não tiver sido concluido, exibe alerta solicitando atualização da data ou conclusão

@dataclass
class Categoria:
    descricao: str
    cor: str
    icone: str
    movimentacoes: list[Movimentacao]
    alertas: list[AlertaCategoria]

@dataclass
class AlertaMovimentacao:
    data: date
    conteudo: str
    movimentacao: Movimentacao
    foi_resolvido: bool

@dataclass
class AlertaCategoria:
    data: date
    conteudo: str
    categoria: Categoria
    foi_resolvido: bool


# LISTA DE DESEJOS
# Lugar onde posso guardar coisas que quero comprar, ou viagens, etc
# Sistema de priorização de cada item (semelhante ao do notion)
# cada item pode se converter em uma movimentação e ganhar uma data_prevista de quando ocorrera
# uma movimentação (não concluida) tambem pode ser mandada para a lista de desejos
# Antes de adicionar na lista de movimentações o sistema faz algumas verificações:
#   - se houver folga no caixa, indica os intervalos recomendados para a movimentação
#   - se não houver, informa ate que data o fluxo ficará negativo se a movimentação for adicionada

# REGISTRAR TODOS OS HISTORICOS DE MOVIMENTAÇÕES