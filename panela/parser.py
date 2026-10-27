"""Analisador sintatico da linguagem Panela.

Descida recursiva escrita a mao, seguindo a gramatica EBNF de
docs/especificacao.md. Dois niveis de precedencia: expressao trata + e -,
termo trata * e /, e o parentese sobe de volta para expressao.
"""

from . import arvore as a
from .erros import ErroSintatico
from .lexer import tokenizar

NOME_AMIGAVEL = {
    "ABRE_CHAVE": "'{'", "FECHA_CHAVE": "'}'", "ABRE_PAR": "'('",
    "FECHA_PAR": "')'", "PONTO_VIRGULA": "';'", "DOIS_PONTOS": "':'",
    "IGUAL": "'='", "IDENT": "um nome", "NUMERO": "um numero",
    "CADEIA": "um texto entre aspas", "UNIDADE": "uma unidade",
    "FAMILIA": "uma familia", "FIM": "o fim do arquivo",
}


def _amigavel(tipo):
    return NOME_AMIGAVEL.get(tipo, f"'{tipo.lower()}'")


class Parser:
    def __init__(self, fonte, arquivo="<entrada>"):
        self.tokens = tokenizar(fonte, arquivo)
        self.i = 0

    # ------------------------------------------------------------- apoio
    @property
    def atual(self):
        return self.tokens[self.i]

    def _e(self, *tipos):
        return self.atual.tipo in tipos

    def _aceitar(self, tipo):
        if self.atual.tipo == tipo:
            tok = self.atual
            self.i += 1
            return tok
        return None

    def _exigir(self, tipo, contexto=""):
        tok = self._aceitar(tipo)
        if tok is None:
            sufixo = f" {contexto}" if contexto else ""
            raise ErroSintatico(
                "PAN-S01",
                f"esperava {_amigavel(tipo)}{sufixo}, "
                f"mas encontrei {_amigavel(self.atual.tipo)}",
                self.atual.pos)
        return tok

    def _contextual(self, palavra):
        """Consome uma palavra-chave contextual ('por', 'a') se ela estiver aqui."""
        if self.atual.tipo == "IDENT" and self.atual.texto == palavra:
            tok = self.atual
            self.i += 1
            return tok
        return None

    def _ident(self, contexto=""):
        """Aceita IDENT e tambem os nomes de familia usados como nome comum."""
        if self._e("IDENT", "FAMILIA"):
            tok = self.atual
            self.i += 1
            return tok
        return self._exigir("IDENT", contexto)

    # ------------------------------------------------------------ receita
    def receita(self):
        inicio = self.atual.pos
        self._exigir("RECEITA", "no inicio do arquivo")
        titulo = self._exigir("CADEIA", "com o nome da receita").valor
        self._exigir("ABRE_CHAVE", "depois do nome da receita")

        self._exigir("RENDE", "logo apos abrir a receita")
        rende_tok = self._exigir("NUMERO", "com o numero de porcoes")
        self._exigir("PORCOES", "depois do numero")
        self._exigir("PONTO_VIRGULA")

        r = a.Receita(titulo=titulo, rende=rende_tok.valor,
                      rende_pos=rende_tok.pos, pos=inicio)

        while self._e("INGREDIENTE"):
            r.ingredientes.append(self.ingrediente())
        while self._e("PREPARO"):
            r.preparos.append(self.preparo())

        self._exigir("MONTAGEM", "depois dos preparos")
        self._exigir("ABRE_CHAVE")
        while not self._e("FECHA_CHAVE"):
            r.montagem.append(self.instrucao())
        self._exigir("FECHA_CHAVE")

        self._exigir("FECHA_CHAVE", "fechando a receita")
        self._exigir("FIM")
        return r

    def ingrediente(self):
        pos = self._exigir("INGREDIENTE").pos
        nome = self._ident("para o ingrediente")
        self._exigir("DOIS_PONTOS", "depois do nome do ingrediente")
        familia = self._exigir("FAMILIA", "para o ingrediente")
        self._exigir("PONTO_VIRGULA")
        return a.Ingrediente(nome.texto, familia.texto, nome.pos)

    def preparo(self):
        pos = self._exigir("PREPARO").pos
        nome = self._ident("para o preparo")
        self._exigir("ABRE_CHAVE", "depois do nome do preparo")
        comandos = []
        while not self._e("FECHA_CHAVE"):
            if self._e("FIM"):
                raise ErroSintatico("PAN-S02",
                                    "o preparo foi aberto e nao foi fechado",
                                    pos)
            comandos.append(self.comando())
        self._exigir("FECHA_CHAVE")
        return a.Preparo(nome.texto, comandos, nome.pos)

    # ----------------------------------------------------------- comandos
    def comando(self):
        if self._e("SEJA"):
            pos = self._exigir("SEJA").pos
            nome = self._ident("depois de 'seja'")
            self._exigir("IGUAL", "depois do nome")
            expr = self.expressao()
            self._exigir("PONTO_VIRGULA")
            return a.Local(nome.texto, expr, nome.pos)

        if self._e("PASSO"):
            return self.passo()

        if self._e("IDENT", "FAMILIA"):
            nome = self._ident()
            self._exigir("IGUAL", "depois do nome do ingrediente")
            expr = self.expressao()
            self._exigir("PONTO_VIRGULA")
            return a.Usa(nome.texto, expr, nome.pos)

        raise ErroSintatico(
            "PAN-S03",
            f"esperava um comando de preparo, mas encontrei "
            f"{_amigavel(self.atual.tipo)}",
            self.atual.pos,
            dica="um preparo aceita 'nome = quantidade;', 'seja ...;' ou 'passo ...;'")

    def passo(self):
        pos = self._exigir("PASSO").pos
        texto = self._exigir("CADEIA", "descrevendo o passo").valor
        duracao = temperatura = None
        if self._contextual("por"):
            duracao = self.expressao()
        if self._contextual("a"):
            temperatura = self.expressao()
        self._exigir("PONTO_VIRGULA")
        return a.Passo(texto, duracao, temperatura, pos)

    # --------------------------------------------------------- instrucoes
    def instrucao(self):
        if self._e("EXECUTAR"):
            pos = self._exigir("EXECUTAR").pos
            nome = self._ident("depois de 'executar'")
            self._exigir("PONTO_VIRGULA")
            return a.Executar(nome.texto, nome.pos)

        if self._e("REPETIR"):
            pos = self._exigir("REPETIR").pos
            vezes = self.expressao()
            self._exigir("VEZES", "depois do numero de repeticoes")
            self._aceitar("EM")
            if self._aceitar("SEQUENCIA"):
                modo = "sequencia"
            elif self._aceitar("PARALELO"):
                modo = "paralelo"
            else:
                raise ErroSintatico(
                    "PAN-S04",
                    "a repeticao precisa dizer se e 'em sequencia' ou 'em paralelo'",
                    self.atual.pos,
                    dica="e isso que decide se o tempo soma ou nao")
            self._exigir("ABRE_CHAVE")
            corpo = []
            while not self._e("FECHA_CHAVE"):
                if self._e("FIM"):
                    raise ErroSintatico("PAN-S02",
                                        "a repeticao foi aberta e nao foi fechada",
                                        pos)
                corpo.append(self.instrucao())
            self._exigir("FECHA_CHAVE")
            return a.Repetir(vezes, modo, corpo, pos)

        raise ErroSintatico(
            "PAN-S05",
            f"esperava 'executar' ou 'repetir', mas encontrei "
            f"{_amigavel(self.atual.tipo)}",
            self.atual.pos)

    # --------------------------------------------------------- expressoes
    def expressao(self):
        no = self.termo()
        while self._e("MAIS", "MENOS"):
            tok = self.atual
            self.i += 1
            no = a.Binaria("+" if tok.tipo == "MAIS" else "-",
                           no, self.termo(), tok.pos)
        return no

    def termo(self):
        no = self.fator()
        while self._e("VEZES_OP", "BARRA"):
            tok = self.atual
            self.i += 1
            no = a.Binaria("*" if tok.tipo == "VEZES_OP" else "/",
                           no, self.fator(), tok.pos)
        return no

    def fator(self):
        tok = self.atual
        if self._aceitar("ABRE_PAR"):
            no = self.expressao()
            self._exigir("FECHA_PAR", "fechando o parentese")
            return no
        if tok.tipo == "NUMERO":
            self.i += 1
            unidade = self._aceitar("UNIDADE")
            return a.Literal(tok.valor,
                             unidade.texto if unidade else None,
                             tok.pos)
        if tok.tipo in ("IDENT", "FAMILIA"):
            self.i += 1
            return a.Nome(tok.texto, tok.pos)
        raise ErroSintatico(
            "PAN-S06",
            f"esperava uma quantidade, um numero ou um nome, mas encontrei "
            f"{_amigavel(tok.tipo)}",
            tok.pos)


def analisar(fonte, arquivo="<entrada>"):
    return Parser(fonte, arquivo).receita()
