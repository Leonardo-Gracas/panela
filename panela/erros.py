"""Erros posicionados da linguagem Panela.

Todo erro carrega arquivo, linha e coluna, como exige o enunciado.
"""


class ErroPanela(Exception):
    """Erro de compilacao com posicao no codigo-fonte."""

    def __init__(self, codigo, mensagem, pos, dica=None):
        self.codigo = codigo
        self.mensagem = mensagem
        self.arquivo = pos.arquivo
        self.linha = pos.linha
        self.coluna = pos.coluna
        self.dica = dica
        super().__init__(self.cabecalho())

    def cabecalho(self):
        return (f"{self.arquivo}:{self.linha}:{self.coluna}: "
                f"erro {self.codigo}: {self.mensagem}")

    def formatar(self, fonte=None):
        linhas = [self.cabecalho()]
        if fonte is not None:
            todas = fonte.splitlines()
            if 0 < self.linha <= len(todas):
                linhas.append(f"  {self.linha:>4} | {todas[self.linha - 1]}")
                linhas.append("       | " + " " * (self.coluna - 1) + "^")
        if self.dica:
            linhas.append(f"  dica: {self.dica}")
        return "\n".join(linhas)


class ErroLexico(ErroPanela):
    pass


class ErroSintatico(ErroPanela):
    pass


class ErroSemantico(ErroPanela):
    pass
