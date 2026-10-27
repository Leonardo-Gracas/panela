"""Quantidades, familias e unidades.

O tipo central da linguagem nao e numero: e quantidade. Toda quantidade
carrega valor, unidade e familia, e a familia decide que operacoes sao
legitimas.
"""

import math
from dataclasses import dataclass

# somavel     -- a familia aceita + e -
# escalavel   -- a familia aceita * e / por numero puro
# auto_escala -- a familia e recalculada quando muda o numero de porcoes
# inteira     -- o valor final precisa ser inteiro (arredonda para cima)
FAMILIAS = {
    "massa":       {"somavel": True,  "escalavel": True,  "auto_escala": True,  "inteira": False},
    "volume":      {"somavel": True,  "escalavel": True,  "auto_escala": True,  "inteira": False},
    "contagem":    {"somavel": True,  "escalavel": True,  "auto_escala": True,  "inteira": True},
    "tempo":       {"somavel": True,  "escalavel": True,  "auto_escala": False, "inteira": False},
    "temperatura": {"somavel": False, "escalavel": False, "auto_escala": False, "inteira": False},
}

# unidade -> (familia, fator para a unidade base da familia)
UNIDADES = {
    "g":   ("massa", 1.0),
    "kg":  ("massa", 1000.0),
    "ml":  ("volume", 1.0),
    "l":   ("volume", 1000.0),
    "xic": ("volume", 240.0),
    "cs":  ("volume", 15.0),
    "cc":  ("volume", 5.0),
    "un":  ("contagem", 1.0),
    "min": ("tempo", 1.0),
    "h":   ("tempo", 60.0),
    "C":   ("temperatura", 1.0),
}

BASE = {"massa": "g", "volume": "ml", "contagem": "un",
        "tempo": "min", "temperatura": "C"}


def familia_de(unidade):
    return UNIDADES[unidade][0]


@dataclass(frozen=True)
class Quantidade:
    """Valor sempre guardado na unidade base da familia."""
    valor: float
    familia: str

    @staticmethod
    def de_literal(valor, unidade):
        familia, fator = UNIDADES[unidade]
        return Quantidade(valor * fator, familia)

    def __add__(self, outra):
        return Quantidade(self.valor + outra.valor, self.familia)

    def __sub__(self, outra):
        return Quantidade(self.valor - outra.valor, self.familia)

    def escalar(self, fator):
        return Quantidade(self.valor * fator, self.familia)

    def arredondada(self):
        """Contagem nao aceita fracao: arredonda para cima."""
        if FAMILIAS[self.familia]["inteira"]:
            return Quantidade(math.ceil(self.valor - 1e-9), self.familia)
        return self


def _numero(valor):
    if abs(valor - round(valor)) < 1e-9:
        return str(int(round(valor)))
    texto = f"{valor:.2f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def formatar(q):
    """Escolhe a unidade mais legivel da familia."""
    v, f = q.valor, q.familia
    if f == "massa":
        return f"{_numero(v / 1000)} kg" if v >= 1000 else f"{_numero(v)} g"
    if f == "volume":
        return f"{_numero(v / 1000)} l" if v >= 1000 else f"{_numero(v)} ml"
    if f == "contagem":
        return f"{_numero(v)} un"
    if f == "tempo":
        return formatar_tempo(v)
    return f"{_numero(v)} C"


def formatar_tempo(minutos):
    minutos = round(minutos)
    if minutos < 60:
        return f"{minutos} min"
    horas, resto = divmod(minutos, 60)
    if resto == 0:
        return f"{horas} h"
    return f"{horas} h {resto} min"
