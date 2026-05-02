from src.application.ports.in.use_cases import CategoriaUseCase
from src.application.ports.out.repositories import CategoriaRepository
from src.domain.entities import Categoria

from src.application.commands.categoria_comands import (
    CriarCategoriaCommand,
    AtualizarCategoriaCommand
)

class CategoriaService(CategoriaUseCase):
    def __init__(self, categoria_repo: CategoriaRepository):
        self.categoria_repo = categoria_repo

    def criar_categoria(self, command: CriarCategoriaCommand) -> Categoria:
        categoria = Categoria(
            descricao=command.descricao,
            cor=command.cor,
            icone=command.icone
        )
        return self.categoria_repo.save(categoria)

    def atualizar_categoria(self, command: AtualizarCategoriaCommand) -> Categoria:
        categoria = self.categoria_repo.find_by_id(command.id)
        if categoria is None:
            raise ValueError("Categoria não encontrada")

        categoria = Categoria(
            id=categoria.id,
            descricao=command.descricao,
            cor=command.cor,
            icone=command.icone
        )
        return self.categoria_repo.save(categoria)

    def deletar_categoria(self, id: int) -> bool:
        categoria = self.categoria_repo.find_by_id(id)
        if categoria is None:
            raise ValueError("Categoria não encontrada")

        return self.categoria_repo.delete(categoria.id)

    def listar_categorias(self) -> list[Categoria]:
        return self.categoria_repo.find_all()
