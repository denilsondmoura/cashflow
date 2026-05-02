from dataclasses import dataclass


@dataclass
class CriarCategoriaCommand:
    descricao: str
    cor: str
    icone: str


@dataclass
class AtualizarCategoriaCommand:
    id: int
    descricao: str
    cor: str
    icone: str

