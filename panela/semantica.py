"""Analise semantica da linguagem Panela.

Tres verificacoes, todas estaticas, todas anteriores a execucao:

  VS1  coerencia de familia   -- so se soma o que pertence a mesma familia
  VS2  operacao permitida     -- cada familia decide se soma e se escala
  VS3  nomes e identidade     -- todo nome usado existe no escopo em que aparece

Escrita a mao, sem biblioteca de analise, como exige o enunciado.
"""

from . import arvore as a
from .erros import ErroSemantico
from .quantidade import FAMILIAS, familia_de

NUMERO = ("numero", None)


def _quantidade(familia):
    return ("quantidade", familia)


def _descrever(tipo):
    return "um numero puro" if tipo[0] == "numero" else f"uma quantidade de {tipo[1]}"


class Analisador:
    """Percorre a arvore inferindo o tipo de cada expressao."""

    def __init__(self, receita):
        self.receita = receita
        self.ingredientes = {}      # nome -> familia
        self.preparos = {}          # nome -> Preparo
        self.escopo = {}            # nome local -> tipo (um por preparo)
        self.avisos = []

    # ------------------------------------------------------------------
    def verificar(self):
        self._declaracoes()
        for p in self.receita.preparos:
            self._preparo(p)
        self._montagem(self.receita.montagem)
        self._nao_usados()
        return self.avisos

    # ------------------------------------------------- VS3: declaracoes
    def _declaracoes(self):
        if self.receita.rende <= 0:
            raise ErroSemantico("PAN-E06",
                                "a receita precisa render pelo menos uma porcao",
                                self.receita.rende_pos)
        for ing in self.receita.ingredientes:
            if ing.nome in self.ingredientes:
                raise ErroSemantico(
                    "PAN-E02",
                    f"o ingrediente '{ing.nome}' ja foi declarado nesta receita",
                    ing.pos)
            self.ingredientes[ing.nome] = ing.familia

        for p in self.receita.preparos:
            if p.nome in self.preparos:
                raise ErroSemantico(
                    "PAN-E02",
                    f"o preparo '{p.nome}' ja foi declarado nesta receita",
                    p.pos)
            self.preparos[p.nome] = p

    def _nao_usados(self):
        executados = set()

        def varrer(insts):
            for i in insts:
                if isinstance(i, a.Executar):
                    executados.add(i.preparo)
                elif isinstance(i, a.Repetir):
                    varrer(i.corpo)

        varrer(self.receita.montagem)
        for nome in self.preparos:
            if nome not in executados:
                self.avisos.append(
                    f"aviso: o preparo '{nome}' nunca e executado na montagem")

    # ---------------------------------------------------------- preparos
    def _preparo(self, preparo):
        self.escopo = {}            # VS3: cada preparo abre um escopo proprio
        for cmd in preparo.comandos:
            self._comando(cmd, preparo)

    def _comando(self, cmd, preparo):
        if isinstance(cmd, a.Usa):
            if cmd.nome not in self.ingredientes:
                raise ErroSemantico(
                    "PAN-E04",
                    f"'{cmd.nome}' nao foi declarado como ingrediente da receita",
                    cmd.pos,
                    dica=f"declare 'ingrediente {cmd.nome} : <familia>;' "
                         f"antes dos preparos, ou use 'seja {cmd.nome} = ...' "
                         f"se for apenas um valor auxiliar")
            if cmd.nome in self.escopo:
                raise ErroSemantico(
                    "PAN-E02",
                    f"'{cmd.nome}' ja recebeu um valor no preparo '{preparo.nome}'",
                    cmd.pos)
            tipo = self._tipo(cmd.expr)
            esperada = self.ingredientes[cmd.nome]
            if tipo[0] == "numero":
                raise ErroSemantico(
                    "PAN-F02",
                    f"'{cmd.nome}' e um ingrediente de {esperada} e nao pode "
                    f"receber um numero sem unidade",
                    cmd.pos)
            if tipo[1] != esperada:
                raise ErroSemantico(
                    "PAN-F05",
                    f"'{cmd.nome}' foi declarado como {esperada}, mas recebeu "
                    f"uma quantidade de {tipo[1]}",
                    cmd.pos)
            self._valor_possivel(cmd, tipo)
            self.escopo[cmd.nome] = tipo

        elif isinstance(cmd, a.Local):
            if cmd.nome in self.escopo:
                raise ErroSemantico(
                    "PAN-E02",
                    f"'{cmd.nome}' ja foi declarado no preparo '{preparo.nome}'",
                    cmd.pos)
            self.escopo[cmd.nome] = self._tipo(cmd.expr)

        elif isinstance(cmd, a.Passo):
            if cmd.duracao is not None:
                tipo = self._tipo(cmd.duracao)
                if tipo != _quantidade("tempo"):
                    raise ErroSemantico(
                        "PAN-F03",
                        f"a duracao de um passo precisa ser tempo, "
                        f"mas aqui e {_descrever(tipo)}",
                        cmd.duracao.pos,
                        dica="use unidades de tempo, como 40 min ou 2 h")
            if cmd.temperatura is not None:
                tipo = self._tipo(cmd.temperatura)
                if tipo != _quantidade("temperatura"):
                    raise ErroSemantico(
                        "PAN-F04",
                        f"a temperatura de um passo precisa ser temperatura, "
                        f"mas aqui e {_descrever(tipo)}",
                        cmd.temperatura.pos,
                        dica="use a unidade C, como 180 C")

    # -------------------------------------------------------- montagem
    def _montagem(self, instrucoes):
        for inst in instrucoes:
            if isinstance(inst, a.Executar):
                if inst.preparo not in self.preparos:
                    raise ErroSemantico(
                        "PAN-E03",
                        f"o preparo '{inst.preparo}' nao foi declarado nesta receita",
                        inst.pos)
            elif isinstance(inst, a.Repetir):
                self.escopo = {}    # a montagem nao enxerga nomes de preparo
                tipo = self._tipo(inst.vezes)
                if tipo[0] != "numero":
                    raise ErroSemantico(
                        "PAN-O05",
                        f"o numero de repeticoes precisa ser um numero puro, "
                        f"mas aqui e {_descrever(tipo)}",
                        inst.vezes.pos,
                        dica="escreva 'repetir 3 vezes', sem unidade")
                vezes = self._constante(inst.vezes)
                if vezes is not None and (vezes < 1 or
                                          abs(vezes - round(vezes)) > 1e-9):
                    raise ErroSemantico(
                        "PAN-C04",
                        f"nao da para repetir {vezes:g} vezes",
                        inst.vezes.pos,
                        dica="o numero de repeticoes precisa ser inteiro e "
                             "pelo menos 1")
                self._montagem(inst.corpo)

    # -------------------------------------------- VS1 e VS2: tipo e algebra
    def _tipo(self, no):
        if isinstance(no, a.Literal):
            if no.unidade is None:
                return NUMERO
            return _quantidade(familia_de(no.unidade))

        if isinstance(no, a.Nome):
            if no.nome not in self.escopo:
                dica = None
                if no.nome in self.ingredientes:
                    dica = (f"'{no.nome}' e ingrediente da receita, mas ainda nao "
                            f"recebeu valor neste preparo")
                raise ErroSemantico(
                    "PAN-E01",
                    f"o nome '{no.nome}' nao existe neste preparo",
                    no.pos, dica=dica)
            return self.escopo[no.nome]

        if isinstance(no, a.Binaria):
            esq = self._tipo(no.esq)
            dir_ = self._tipo(no.dir)
            if no.op in "+-":
                return self._aditiva(no, esq, dir_)
            return self._multiplicativa(no, esq, dir_)

        raise AssertionError(f"no desconhecido: {no!r}")

    def _aditiva(self, no, esq, dir_):
        verbo = "somar" if no.op == "+" else "subtrair"
        if esq[0] == "numero" and dir_[0] == "numero":
            return NUMERO
        if esq[0] == "numero" or dir_[0] == "numero":
            quantidade = dir_ if esq[0] == "numero" else esq
            raise ErroSemantico(
                "PAN-F02",
                f"nao da para {verbo} {_descrever(esq)} com {_descrever(dir_)}",
                no.pos,
                dica=f"um numero sem unidade nao tem familia; escreva a unidade "
                     f"de {quantidade[1]}")
        if esq[1] != dir_[1]:
            raise ErroSemantico(
                "PAN-F01",
                f"nao da para {verbo} {esq[1]} com {dir_[1]}",
                no.pos,
                dica="so quantidades da mesma familia podem ser somadas")
        if not FAMILIAS[esq[1]]["somavel"]:
            raise ErroSemantico(
                "PAN-O01",
                f"a familia {esq[1]} nao e somavel",
                no.pos,
                dica="temperatura e um ponto numa escala, nao uma quantidade "
                     "que se acumula")
        return esq

    def _multiplicativa(self, no, esq, dir_):
        verbo = "multiplicar" if no.op == "*" else "dividir"

        if esq[0] == "numero" and dir_[0] == "numero":
            return NUMERO

        # quantidade / quantidade da mesma familia -> proporcao (numero puro)
        if no.op == "/" and esq[0] == "quantidade" and dir_[0] == "quantidade":
            if esq[1] != dir_[1]:
                raise ErroSemantico(
                    "PAN-F01",
                    f"nao da para dividir {esq[1]} por {dir_[1]}",
                    no.pos,
                    dica="a divisao entre familias diferentes nao esta definida")
            return NUMERO

        if esq[0] == "quantidade" and dir_[0] == "quantidade":
            raise ErroSemantico(
                "PAN-O03",
                f"nao da para multiplicar {_descrever(esq)} por {_descrever(dir_)}",
                no.pos,
                dica="escalar e sempre quantidade vezes um numero puro")

        if no.op == "/" and esq[0] == "numero":
            raise ErroSemantico(
                "PAN-O04",
                f"nao da para dividir um numero puro por {_descrever(dir_)}",
                no.pos)

        quantidade = esq if esq[0] == "quantidade" else dir_
        if not FAMILIAS[quantidade[1]]["escalavel"]:
            raise ErroSemantico(
                "PAN-O02",
                f"a familia {quantidade[1]} nao pode ser escalada",
                no.pos,
                dica="dobrar a receita nao dobra a temperatura do forno")
        return quantidade


    # ---------------------------------------- VS4: valores impossiveis
    def _constante(self, no):
        """Dobra expressoes feitas so de literais. Devolve valor ou None.

        Serve para pegar, antes de executar, quantidades negativas, divisao
        por zero e fracao em contagem -- desde que a expressao nao dependa
        de nome nenhum.
        """
        if isinstance(no, a.Literal):
            if no.unidade is None:
                return no.valor
            from .quantidade import UNIDADES
            return no.valor * UNIDADES[no.unidade][1]
        if isinstance(no, a.Binaria):
            esq = self._constante(no.esq)
            dir_ = self._constante(no.dir)
            if esq is None or dir_ is None:
                return None
            if no.op == "+":
                return esq + dir_
            if no.op == "-":
                return esq - dir_
            if no.op == "*":
                return esq * dir_
            if dir_ == 0:
                raise ErroSemantico("PAN-C03", "divisao por zero", no.pos)
            return esq / dir_
        return None

    def _valor_possivel(self, cmd, tipo):
        valor = self._constante(cmd.expr)
        if valor is None:
            return
        familia = tipo[1]
        if familia == "temperatura":
            return
        if valor <= 0:
            raise ErroSemantico(
                "PAN-C02",
                f"'{cmd.nome}' ficou com quantidade {'negativa' if valor < 0 else 'zero'}",
                cmd.pos,
                dica="uma receita nao usa quantidade nula nem negativa")
        if FAMILIAS[familia]["inteira"] and abs(valor - round(valor)) > 1e-9:
            raise ErroSemantico(
                "PAN-C01",
                f"'{cmd.nome}' e de contagem e ficou com valor fracionario "
                f"({valor:g})",
                cmd.pos,
                dica="contagem nao aceita fracao na propria receita; "
                     "o arredondamento so acontece ao escalar porcoes")


def verificar(receita):
    """Roda as verificacoes. Devolve a lista de avisos."""
    return Analisador(receita).verificar()
