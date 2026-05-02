
# FLUXO DE CAIXA

# Planejamento
- planejar_ate
- valor_diaria currency
- total_orcado currency
- orcamentos many to many Orcamento
- movimentacoes many to many Movimentacao

# Orcamento
- saldo_atual currency
- saldo_previsto currency
- categoria foreign key Categoria

# Movimentacao
- data_prevista date
- descricao str
- valor currency
- foi_concluida bool
- data_conclusao date
- categoria foreign key Categoria
- eh_debito_automatico bool
- repetir bool
- qtd_repeticoes
- repetir_ate date
- alertas many to many AlertaMovimentacao

+ Sempre que uma movimentação for criada verificar se a meta_mensal da categoria não foi batida. Se foi, gerar alerta
+ Se chegar a data_prevista e ainda não tiver sido concluido, exibe alerta solicitando atualização da data ou conclusão

# Categoria
- descricao str
- cor str
- icone str
- movimentacoes many to many Movimentacao
- alertas many to many AlertaCategoria

# AlertaMovimentacao
- data date
- conteudo str
- movimentacao foreign key Movimentacao
- foi_resolvido bool

# AlertaCategoria
- data date
- conteudo str
- categoria foreign key Categoria
- foi_resolvido bool


# LISTA DE DESEJOS
+ Lugar onde posso guardar coisas que quero comprar, ou viagens, etc
+ Sistema de priorização de cada item (semelhante ao do notion)
+ cada item pode se converter em uma movimentação e ganhar uma data_prevista de quando ocorrera
+ uma movimentação (não concluida) tambem pode ser mandada para a lista de desejos
+ Antes de adicionar na lista de movimentações o sistema faz algumas verificações:
    + se houver folga no caixa, indica os intervalos recomendados para a movimentação
    + se não houver, informa ate que data o fluxo ficará negativo se a movimentação for adicionada

# REGISTRAR TODOS OS HISTORICOS DE MOVIMENTAÇÕES