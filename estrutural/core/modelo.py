"""Domínio independente de Qt. Unidades internas futuras: kN e m."""
from dataclasses import dataclass, field
from enum import Enum


class Tipologia(str, Enum):
    VIGA = 'Viga'
    PORTICO = 'Pórtico plano'
    TRELICA = 'Treliça'
    GRELHA = 'Grelha'
    ARCO = 'Arco'

    @property
    def graus_de_liberdade(self):
        if self is Tipologia.TRELICA:
            return ('u', 'v')
        if self is Tipologia.GRELHA:
            return ('w', 'θx', 'θy')
        return ('u', 'v', 'θ')


@dataclass
class Projeto:
    nome: str = 'Sem título'
    tipologia: Tipologia = Tipologia.PORTICO
    nos: dict = field(default_factory=dict)
    barras: dict = field(default_factory=dict)
