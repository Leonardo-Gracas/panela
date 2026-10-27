"""Analisador lexico da linguagem Panela.

Escrito a mao. Cada token carrega arquivo, linha e coluna, porque toda
mensagem de erro da linguagem precisa estar posicionada.
"""

from dataclasses import dataclass

from .erros import ErroLexico
from .quantidade import UNIDADES

# Palavras reservadas da linguagem.
PALAVRAS = {
    "receita", "rende", "porcoes", "ingrediente", "preparo", "seja",
    "passo", "repetir", "vezes", "em", "sequencia", "paralelo",
    "executar", "montagem",
}

# Palavras-chave contextuais: so valem como palavra-chave na posicao em que
# o parser as espera. Fora dela sao nomes comuns, o que permite escrever
# 'preparo a { ... }' sem conflito com 'passo "x" a 180 C'.
CONTEXTUAIS = {"por", "a"}

FAMILIAS_TOKEN = {"massa", "volume", "contagem", "tempo", "temperatura"}

SIMBOLOS = {
    "{": "ABRE_CHAVE", "}": "FECHA_CHAVE", "(": "ABRE_PAR", ")": "FECHA_PAR",
    ";": "PONTO_VIRGULA", ",": "VIRGULA", ":": "DOIS_PONTOS", "=": "IGUAL",
    "+": "MAIS", "-": "MENOS", "*": "VEZES_OP", "/": "BARRA",
}


@dataclass(frozen=True)
class Pos:
    arquivo: str
    linha: int
    coluna: int

    def __str__(self):
        return f"{self.arquivo}:{self.linha}:{self.coluna}"


@dataclass(frozen=True)
class Token:
    tipo: str
    texto: str
    pos: Pos
    valor: object = None

    def __str__(self):
        return f"{self.tipo}({self.texto})"


class Lexer:
    def __init__(self, fonte, arquivo="<entrada>"):
        self.fonte = fonte
        self.arquivo = arquivo
        self.i = 0
        self.linha = 1
        self.coluna = 1

    # ------------------------------------------------------------------
    def _pos(self):
        return Pos(self.arquivo, self.linha, self.coluna)

    def _atual(self):
        return self.fonte[self.i] if self.i < len(self.fonte) else ""

    def _espiar(self, n=1):
        j = self.i + n
        return self.fonte[j] if j < len(self.fonte) else ""

    def _avancar(self):
        c = self.fonte[self.i]
        self.i += 1
        if c == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    # ------------------------------------------------------------------
    def tokens(self):
        saida = []
        while True:
            self._pular_ignoraveis()
            if self.i >= len(self.fonte):
                saida.append(Token("FIM", "", self._pos()))
                return saida
            saida.append(self._proximo())

    def _pular_ignoraveis(self):
        while self.i < len(self.fonte):
            c = self._atual()
            if c in " \t\r\n":
                self._avancar()
            elif c == "/" and self._espiar() == "/":
                while self.i < len(self.fonte) and self._atual() != "\n":
                    self._avancar()
            elif c == "/" and self._espiar() == "*":
                abertura = self._pos()
                self._avancar()
                self._avancar()
                while True:
                    if self.i >= len(self.fonte):
                        raise ErroLexico("PAN-L03",
                                         "comentario de bloco nao foi fechado",
                                         abertura)
                    if self._atual() == "*" and self._espiar() == "/":
                        self._avancar()
                        self._avancar()
                        break
                    self._avancar()
            else:
                return

    def _proximo(self):
        pos = self._pos()
        c = self._atual()

        if c.isdigit():
            return self._numero(pos)
        if c.isalpha() or c == "_":
            return self._palavra(pos)
        if c == '"':
            return self._cadeia(pos)
        if c in SIMBOLOS:
            self._avancar()
            return Token(SIMBOLOS[c], c, pos)

        self._avancar()
        raise ErroLexico("PAN-L01", f"caractere inesperado {c!r}", pos)

    def _numero(self, pos):
        texto = ""
        while self._atual().isdigit():
            texto += self._avancar()
        if self._atual() == "." and self._espiar().isdigit():
            texto += self._avancar()
            while self._atual().isdigit():
                texto += self._avancar()
        return Token("NUMERO", texto, pos, float(texto))

    def _palavra(self, pos):
        texto = ""
        while self._atual().isalnum() or self._atual() == "_":
            texto += self._avancar()
        if texto in UNIDADES:
            return Token("UNIDADE", texto, pos)
        if texto in PALAVRAS:
            return Token(texto.upper(), texto, pos)
        if texto in FAMILIAS_TOKEN:
            return Token("FAMILIA", texto, pos)
        return Token("IDENT", texto, pos)

    def _cadeia(self, pos):
        self._avancar()  # aspa de abertura
        texto = ""
        while True:
            if self.i >= len(self.fonte) or self._atual() == "\n":
                raise ErroLexico("PAN-L02", "texto nao foi fechado com aspas", pos)
            c = self._avancar()
            if c == '"':
                return Token("CADEIA", texto, pos, texto)
            if c == "\\" and self._atual() == '"':
                texto += self._avancar()
            else:
                texto += c


def tokenizar(fonte, arquivo="<entrada>"):
    return Lexer(fonte, arquivo).tokens()
