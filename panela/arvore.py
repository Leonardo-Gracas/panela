"""Arvore sintatica abstrata da linguagem Panela."""

from dataclasses import dataclass, field
from typing import List, Optional

from .lexer import Pos


# --------------------------------------------------------------- expressoes
@dataclass
class Literal:
    valor: float
    unidade: Optional[str]      # None  ->  numero puro
    pos: Pos


@dataclass
class Nome:
    nome: str
    pos: Pos


@dataclass
class Binaria:
    op: str
    esq: object
    dir: object
    pos: Pos


# ----------------------------------------------------------------- comandos
@dataclass
class Usa:
    """nome = expressao;  dentro de um preparo (nome de ingrediente)."""
    nome: str
    expr: object
    pos: Pos


@dataclass
class Local:
    """seja nome = expressao;  nome auxiliar, nao vai para a lista de compras."""
    nome: str
    expr: object
    pos: Pos


@dataclass
class Passo:
    texto: str
    duracao: Optional[object]
    temperatura: Optional[object]
    pos: Pos


# -------------------------------------------------------------- instrucoes
@dataclass
class Executar:
    preparo: str
    pos: Pos


@dataclass
class Repetir:
    vezes: object
    modo: str                   # "sequencia" | "paralelo"
    corpo: List[object]
    pos: Pos


# --------------------------------------------------------------- estruturas
@dataclass
class Ingrediente:
    nome: str
    familia: str
    pos: Pos


@dataclass
class Preparo:
    nome: str
    comandos: List[object]
    pos: Pos


@dataclass
class Receita:
    titulo: str
    rende: float
    rende_pos: Pos
    ingredientes: List[Ingrediente] = field(default_factory=list)
    preparos: List[Preparo] = field(default_factory=list)
    montagem: List[object] = field(default_factory=list)
    pos: Pos = None


# ------------------------------------------------------ impressao da arvore
def imprimir(no, nivel=0):
    """Dump textual da arvore, exigido no Checkpoint 1."""
    espaco = "  " * nivel
    if isinstance(no, Receita):
        linhas = [f'{espaco}Receita "{no.titulo}" (rende {no.rende:g} porcoes)']
        for i in no.ingredientes:
            linhas.append(f"{espaco}  Ingrediente {i.nome} : {i.familia}")
        for p in no.preparos:
            linhas.append(imprimir(p, nivel + 1))
        linhas.append(f"{espaco}  Montagem")
        for inst in no.montagem:
            linhas.append(imprimir(inst, nivel + 2))
        return "\n".join(linhas)
    if isinstance(no, Preparo):
        linhas = [f"{espaco}Preparo {no.nome}"]
        for c in no.comandos:
            linhas.append(imprimir(c, nivel + 1))
        return "\n".join(linhas)
    if isinstance(no, Usa):
        return f"{espaco}Usa {no.nome}\n{imprimir(no.expr, nivel + 1)}"
    if isinstance(no, Local):
        return f"{espaco}Local {no.nome}\n{imprimir(no.expr, nivel + 1)}"
    if isinstance(no, Passo):
        linhas = [f'{espaco}Passo "{no.texto}"']
        if no.duracao is not None:
            linhas.append(f"{espaco}  por")
            linhas.append(imprimir(no.duracao, nivel + 2))
        if no.temperatura is not None:
            linhas.append(f"{espaco}  a")
            linhas.append(imprimir(no.temperatura, nivel + 2))
        return "\n".join(linhas)
    if isinstance(no, Executar):
        return f"{espaco}Executar {no.preparo}"
    if isinstance(no, Repetir):
        linhas = [f"{espaco}Repetir em {no.modo}", imprimir(no.vezes, nivel + 1)]
        for c in no.corpo:
            linhas.append(imprimir(c, nivel + 1))
        return "\n".join(linhas)
    if isinstance(no, Binaria):
        return (f"{espaco}{no.op}\n"
                f"{imprimir(no.esq, nivel + 1)}\n"
                f"{imprimir(no.dir, nivel + 1)}")
    if isinstance(no, Literal):
        if no.unidade is None:
            return f"{espaco}Numero {no.valor:g}"
        return f"{espaco}Quantidade {no.valor:g} {no.unidade}"
    if isinstance(no, Nome):
        return f"{espaco}Nome {no.nome}"
    return f"{espaco}{no!r}"
