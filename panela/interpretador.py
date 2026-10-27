"""Execucao da linguagem Panela.

Avalia a receita para um numero de porcoes e produz a saida em Markdown,
com a lista de compras somada entre os preparos e o tempo total.

Escalar: toda quantidade literal de familia auto-escalavel (massa, volume,
contagem) e multiplicada pelo fator de porcoes no momento em que e lida.
Tempo e temperatura ficam intactos -- e por isso que a receita escala sem
estragar.
"""

from collections import OrderedDict

from . import arvore as a
from .quantidade import FAMILIAS, Quantidade, formatar, formatar_tempo


class Preparado:
    """Resultado de executar um preparo uma vez."""

    def __init__(self, nome):
        self.nome = nome
        self.ingredientes = OrderedDict()   # nome -> Quantidade
        self.passos = []                    # (texto, duracao|None, temp|None)
        self.tempo = 0.0                    # minutos


class Interpretador:
    def __init__(self, receita, porcoes=None):
        self.receita = receita
        self.porcoes = porcoes if porcoes is not None else receita.rende
        self.fator = self.porcoes / receita.rende
        self.familia_de_ingrediente = {i.nome: i.familia
                                       for i in receita.ingredientes}
        self.escopo = {}

    # ------------------------------------------------------------ execucao
    def executar(self):
        preparados = OrderedDict()
        for p in self.receita.preparos:
            preparados[p.nome] = self._preparo(p)

        compras = OrderedDict()
        for nome in self.familia_de_ingrediente:
            compras[nome] = None

        tempo_total = self._montagem(self.receita.montagem, preparados, compras)
        compras = OrderedDict((n, q) for n, q in compras.items() if q is not None)
        return preparados, compras, tempo_total

    def _preparo(self, preparo):
        self.escopo = {}
        feito = Preparado(preparo.nome)
        for cmd in preparo.comandos:
            if isinstance(cmd, a.Usa):
                q = self._valor(cmd.expr).arredondada()
                self.escopo[cmd.nome] = q
                feito.ingredientes[cmd.nome] = q
            elif isinstance(cmd, a.Local):
                self.escopo[cmd.nome] = self._valor(cmd.expr)
            elif isinstance(cmd, a.Passo):
                dur = self._valor(cmd.duracao) if cmd.duracao is not None else None
                temp = (self._valor(cmd.temperatura)
                        if cmd.temperatura is not None else None)
                feito.passos.append((cmd.texto, dur, temp))
                if dur is not None:
                    feito.tempo += dur.valor
        return feito

    def _montagem(self, instrucoes, preparados, compras, multiplicador=1.0):
        tempo = 0.0
        for inst in instrucoes:
            if isinstance(inst, a.Executar):
                feito = preparados[inst.preparo]
                for nome, q in feito.ingredientes.items():
                    parcela = q.escalar(multiplicador)
                    atual = compras.get(nome)
                    compras[nome] = parcela if atual is None else atual + parcela
                tempo += feito.tempo
            elif isinstance(inst, a.Repetir):
                vezes = self._numero(inst.vezes)
                interno = self._montagem(inst.corpo, preparados, compras,
                                         multiplicador * vezes)
                # em sequencia o tempo se repete; em paralelo acontece uma vez so
                tempo += interno * (vezes if inst.modo == "sequencia" else 1)
        return tempo

    # ------------------------------------------------------------- valores
    def _valor(self, no):
        if isinstance(no, a.Literal):
            if no.unidade is None:
                return no.valor
            q = Quantidade.de_literal(no.valor, no.unidade)
            if FAMILIAS[q.familia]["auto_escala"]:
                q = q.escalar(self.fator)
            return q
        if isinstance(no, a.Nome):
            return self.escopo[no.nome]
        if isinstance(no, a.Binaria):
            esq = self._valor(no.esq)
            dir_ = self._valor(no.dir)
            return self._operar(no.op, esq, dir_)
        raise AssertionError(f"no desconhecido: {no!r}")

    def _numero(self, no):
        v = self._valor(no)
        return v.valor if isinstance(v, Quantidade) else v

    @staticmethod
    def _operar(op, esq, dir_):
        eq, dq = isinstance(esq, Quantidade), isinstance(dir_, Quantidade)
        if op == "+":
            return esq + dir_ if eq else esq + dir_
        if op == "-":
            return esq - dir_ if eq else esq - dir_
        if op == "*":
            if eq and not dq:
                return esq.escalar(dir_)
            if dq and not eq:
                return dir_.escalar(esq)
            return esq * dir_
        if op == "/":
            if eq and dq:
                return esq.valor / dir_.valor
            if eq:
                return esq.escalar(1.0 / dir_)
            return esq / dir_
        raise AssertionError(op)


# --------------------------------------------------------------- markdown
def gerar_markdown(receita, porcoes=None):
    interp = Interpretador(receita, porcoes)
    preparados, compras, tempo_total = interp.executar()
    familias = interp.familia_de_ingrediente

    linhas = [f"# {receita.titulo}", ""]
    linhas.append(f"**Rende:** {_porcoes(interp.porcoes)}  ")
    linhas.append(f"**Tempo total:** {formatar_tempo(tempo_total)}")
    if abs(interp.fator - 1.0) > 1e-9:
        linhas.append("")
        linhas.append(f"> Receita escalada por {_fator(interp.fator)} a partir "
                      f"de {_porcoes(receita.rende)}. "
                      f"Tempos e temperaturas nao foram escalados.")
    linhas.append("")

    linhas.append("## Lista de compras")
    linhas.append("")
    if not compras:
        linhas.append("_Nenhum ingrediente usado._")
    for nome, q in compras.items():
        linhas.append(f"- **{nome}** — {formatar(q.arredondada())}")
    linhas.append("")

    for nome, feito in preparados.items():
        linhas.append(f"## {nome.capitalize()}")
        linhas.append("")
        if feito.ingredientes:
            for ing, q in feito.ingredientes.items():
                linhas.append(f"- {ing} — {formatar(q)}")
            linhas.append("")
        if feito.passos:
            for n, (texto, dur, temp) in enumerate(feito.passos, 1):
                extras = []
                if dur is not None:
                    extras.append(formatar(dur))
                if temp is not None:
                    extras.append(f"a {formatar(temp)}")
                sufixo = f" _({', '.join(extras)})_" if extras else ""
                linhas.append(f"{n}. {texto}{sufixo}")
            linhas.append("")

    linhas.append("## Montagem")
    linhas.append("")
    linhas.extend(_montagem_texto(receita.montagem, 0))
    linhas.append("")
    return "\n".join(linhas).rstrip() + "\n"


def _montagem_texto(instrucoes, nivel):
    saida = []
    recuo = "    " * nivel
    for inst in instrucoes:
        if isinstance(inst, a.Executar):
            saida.append(f"{recuo}- {inst.preparo.capitalize()}")
        elif isinstance(inst, a.Repetir):
            vezes = inst.vezes.valor if isinstance(inst.vezes, a.Literal) else "?"
            modo = "em sequencia" if inst.modo == "sequencia" else "em paralelo"
            saida.append(f"{recuo}- Repetir {vezes:g} vezes {modo}:")
            saida.extend(_montagem_texto(inst.corpo, nivel + 1))
    return saida


def _porcoes(n):
    inteiro = int(round(n))
    return f"{inteiro} porcao" if inteiro == 1 else f"{inteiro} porcoes"


def _fator(f):
    if abs(f - round(f)) < 1e-9:
        return f"{int(round(f))}x"
    return f"{f:.2f}x".replace(".", ",")
