"""Linha de comando da linguagem Panela.

    python -m panela receita.pan
    python -m panela receita.pan --porcoes 24
    python -m panela receita.pan --arvore
    python -m panela receita.pan -o receita.md
"""

import argparse
import sys

from .arvore import imprimir
from .erros import ErroPanela
from .interpretador import gerar_markdown
from .parser import analisar
from .semantica import verificar


def compilar(fonte, arquivo="<entrada>"):
    """Le, analisa e verifica. Devolve (receita, avisos)."""
    receita = analisar(fonte, arquivo)
    avisos = verificar(receita)
    return receita, avisos


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="panela",
        description="Compilador da linguagem Panela — receitas que escalam.")
    p.add_argument("arquivo", help="arquivo .pan a compilar")
    p.add_argument("--porcoes", type=float, default=None,
                   help="recalcula a receita para este numero de porcoes")
    p.add_argument("--arvore", action="store_true",
                   help="imprime a arvore sintatica e para")
    p.add_argument("--so-verificar", action="store_true",
                   help="roda as verificacoes e nao executa")
    p.add_argument("-o", "--saida", default=None,
                   help="grava o Markdown em um arquivo")
    args = p.parse_args(argv)

    try:
        with open(args.arquivo, encoding="utf-8") as f:
            fonte = f.read()
    except OSError as e:
        print(f"panela: nao consegui abrir {args.arquivo}: {e}", file=sys.stderr)
        return 2

    try:
        if args.arvore:
            from .parser import analisar as _analisar
            print(imprimir(_analisar(fonte, args.arquivo)))
            return 0
        receita, avisos = compilar(fonte, args.arquivo)
    except ErroPanela as e:
        print(e.formatar(fonte), file=sys.stderr)
        return 1

    for aviso in avisos:
        print(aviso, file=sys.stderr)

    if args.so_verificar:
        print(f"{args.arquivo}: ok")
        return 0

    md = gerar_markdown(receita, args.porcoes)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"gravado em {args.saida}")
    else:
        print(md, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
