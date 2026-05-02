from datetime import date
from dataclasses import dataclass


@dataclass
class CriarPlanejamentoCommand:
    planejar_ate: date


@dataclass
class AtualizarPlanejamentoCommand:
    id: int
    planejar_ate: date
