"""Mede a eficacia da verificacao semantica (opcao B do enunciado).

Roda todo o corpus, compara o codigo de erro observado com o declarado no
cabecalho de cada arquivo e imprime a tabela de resultados em Markdown.

    python avaliacao/medir.py
    python avaliacao/medir.py --detalhe
"""

import argparse
import os
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panela.cli import compilar          # noqa: E402
from panela.erros import ErroPanela      # noqa: E402

CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus")

CATEGORIAS = OrderedDict([
    ("VS1", "Coerencia de familia"),
    ("VS2", "Operacao propria da familia"),
    ("VS3", "Nomes e identidade"),
    ("VS4", "Valores impossiveis no dominio"),
    ("limite", "Limites conhecidos (fora do alcance atual)"),
    ("controle", "Programas corretos (controle)"),
])


def ler_cabecalho(fonte):
    categoria = esperado = None
    for linha in fonte.splitlines():
        if linha.startswith("// CATEGORIA:"):
            categoria = linha.split(":", 1)[1].strip()
        elif linha.startswith("// ESPERADO:"):
            valor = linha.split(":", 1)[1].strip()
            esperado = None if valor == "nenhum" else valor
        if categoria and linha.startswith("receita"):
            break
    return categoria, esperado


def rodar_um(caminho):
    with open(caminho, encoding="utf-8") as f:
        fonte = f.read()
    categoria, esperado = ler_cabecalho(fonte)
    try:
        compilar(fonte, os.path.basename(caminho))
        obtido = None
    except ErroPanela as e:
        obtido = e.codigo

    if esperado is None:
        resultado = "ok" if obtido is None else "falso positivo"
    elif obtido is None:
        resultado = "escapou"
    elif obtido == esperado:
        resultado = "detectado"
    else:
        resultado = "detectado (codigo diferente)"
    return categoria, esperado, obtido, resultado


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--detalhe", action="store_true",
                   help="lista o resultado caso a caso")
    args = p.parse_args()

    arquivos = sorted(f for f in os.listdir(CORPUS) if f.endswith(".pan"))
    if not arquivos:
        print("corpus vazio — rode antes: python avaliacao/gerar_corpus.py")
        return 1

    por_categoria = {c: Counter() for c in CATEGORIAS}
    detalhes = []

    for nome in arquivos:
        categoria, esperado, obtido, resultado = rodar_um(
            os.path.join(CORPUS, nome))
        por_categoria.setdefault(categoria, Counter())[resultado] += 1
        detalhes.append((nome, categoria, esperado, obtido, resultado))

    print("# Avaliacao da verificacao semantica\n")
    print(f"Corpus: {len(arquivos)} programas "
          f"({sum(1 for d in detalhes if d[2] is not None)} com erro proposital, "
          f"{sum(1 for d in detalhes if d[2] is None)} corretos).\n")

    print("| Categoria | Casos | Detectados | Escaparam | Falsos positivos | Taxa |")
    print("|---|---|---|---|---|---|")
    total = Counter()
    for cat, titulo in CATEGORIAS.items():
        c = por_categoria.get(cat, Counter())
        casos = sum(c.values())
        if not casos:
            continue
        det = c["detectado"] + c["detectado (codigo diferente)"]
        esc = c["escapou"]
        fp = c["falso positivo"]
        total.update(c)
        if cat == "controle":
            taxa = f"{(c['ok'] / casos) * 100:.0f}% sem alarme falso"
        else:
            taxa = f"{(det / casos) * 100:.0f}%"
        print(f"| {titulo} | {casos} | {det} | {esc} | {fp} | {taxa} |")

    casos = sum(total.values())
    det = total["detectado"] + total["detectado (codigo diferente)"]
    print(f"| **Total** | **{casos}** | **{det}** | **{total['escapou']}** "
          f"| **{total['falso positivo']}** | — |")

    divergentes = [d for d in detalhes if d[4] == "detectado (codigo diferente)"]
    if divergentes:
        print("\n## Detectados com codigo diferente do previsto\n")
        for nome, _, esperado, obtido, _ in divergentes:
            print(f"- `{nome}`: previsto {esperado}, obtido {obtido}")

    problemas = [d for d in detalhes if d[4] in ("escapou", "falso positivo")]
    if problemas:
        print("\n## Casos problematicos\n")
        for nome, _, esperado, obtido, resultado in problemas:
            print(f"- `{nome}`: {resultado} (previsto {esperado}, obtido {obtido})")

    if args.detalhe:
        print("\n## Caso a caso\n")
        print("| Arquivo | Categoria | Previsto | Obtido | Resultado |")
        print("|---|---|---|---|---|")
        for nome, cat, esperado, obtido, resultado in detalhes:
            print(f"| `{nome}` | {cat} | {esperado or '—'} "
                  f"| {obtido or '—'} | {resultado} |")

    return 0


if __name__ == "__main__":
    sys.exit(main())
