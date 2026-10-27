# Panela

Linguagem de domínio específico para escrever receitas que escalam sem erro.

Dobrar uma receita não é multiplicar tudo: a farinha dobra, a temperatura do
forno não, e `3 ovos × 1,5` não dá `4,5 ovos`. Panela trata quantidade como tipo
— valor, unidade e **família** — e recusa, antes de executar, as operações que a
família não permite.

```panela
receita "Bolo de cenoura" {
  rende 12 porcoes;

  ingrediente acucar  : massa;
  ingrediente ovo     : contagem;

  preparo massa {
    acucar = 200 g;
    ovo    = 3 un;
    passo "Assar" por 40 min a 180 C;
  }

  preparo cobertura {
    acucar = 50 g;            // mesmo nome, outro escopo
    passo "Derreter" por 8 min;
  }

  montagem {
    executar massa;
    executar cobertura;
  }
}
```

```
$ python -m panela exemplos/bolo.pan --porcoes 24
```

A saída é a receita em Markdown, com a lista de compras somada entre os preparos
(`acucar` aparece uma vez, com 500 g) e o tempo total calculado. Massas, volumes
e contagens são escalados; tempos e temperaturas não.

---

## Instalação

Python 3.10 ou superior. Sem dependências para executar a linguagem.

```bash
git clone <url-do-repositorio>
cd panela
python -m panela exemplos/bolo.pan
```

Para rodar os testes:

```bash
pip install pytest
python -m pytest tests/ -q
```

## Uso

```bash
python -m panela receita.pan                 # imprime a receita em Markdown
python -m panela receita.pan --porcoes 24    # recalcula para outro rendimento
python -m panela receita.pan -o receita.md   # grava em arquivo
python -m panela receita.pan --arvore        # imprime a árvore sintática
python -m panela receita.pan --so-verificar  # só roda as verificações
```

## A linguagem em uma página

**Famílias.** Toda quantidade pertence a uma das cinco famílias, e a família
decide o que é legítimo:

| Família | Unidades | Soma | Escala | Escala por porções |
|---|---|---|---|---|
| massa | `g` `kg` | sim | sim | sim |
| volume | `ml` `l` `xic` `cs` `cc` | sim | sim | sim |
| contagem | `un` | sim | sim | sim, arredondando para cima |
| tempo | `min` `h` | sim | sim | **não** |
| temperatura | `C` | **não** | **não** | **não** |

**Escopo.** Cada `preparo` abre um escopo próprio. `massa.acucar` e
`cobertura.acucar` são nomes diferentes e não colidem, mas a identidade do
ingrediente é global — declarada uma vez com `ingrediente` — e é por isso que os
dois viram uma linha só na lista de compras. `seja` cria um nome auxiliar que
não vai às compras.

**Precedência.** `*` e `/` antes de `+` e `-`; parênteses mandam. Escalar é
sempre quantidade × número puro: `200 g * 2 g` é erro.

**Repetição.** `repetir N vezes em sequencia` multiplica ingredientes **e**
tempo; `em paralelo` multiplica só os ingredientes. Três camadas no mesmo forno
gastam três vezes a massa e assam uma vez.

## Verificações semânticas

Quatro grupos, todos estáticos, todos com arquivo, linha e coluna na mensagem:

- **VS1 — coerência de família** (`PAN-F01`–`PAN-F05`): somar massa com tempo,
  duração que não é tempo, ingrediente que recebe a família errada.
- **VS2 — operação própria da família** (`PAN-O01`–`PAN-O05`): somar ou escalar
  temperatura, multiplicar quantidade por quantidade, repetir um número de vezes
  que não é número puro.
- **VS3 — nomes e identidade** (`PAN-E01`–`PAN-E06`): nome inexistente no
  escopo, declaração duplicada, `executar` de preparo que não existe.
- **VS4 — valores impossíveis** (`PAN-C01`–`PAN-C04`): quantidade negativa ou
  zero, fração em contagem, divisão por zero, repetição fracionária.

```
$ python -m panela exemplos/rejeitados/soma_incompativel.pan
exemplos/rejeitados/soma_incompativel.pan:8:20: erro PAN-F01: nao da para somar massa com tempo
     8 |     farinha = 200 g + 30 min;
       |                     ^
  dica: so quantidades da mesma familia podem ser somadas
```

## Estrutura do repositório

```
panela/
  panela/            implementação
    lexer.py         análise léxica, com posição em todo token
    parser.py        descida recursiva, dois níveis de precedência
    arvore.py        nós da AST e impressão da árvore
    semantica.py     as quatro verificações
    interpretador.py execução, escala e geração do Markdown
    quantidade.py    famílias, unidades e conversão interna
    erros.py         erro posicionado (arquivo, linha, coluna)
    cli.py           linha de comando
  exemplos/          três programas que executam
    rejeitados/      três programas corretamente recusados
  tests/             testes automatizados (pytest)
  avaliacao/         corpus e medição da verificação semântica
  docs/
    especificacao.md propósito, EBNF, tokens, verificações
```

## Avaliação

A seção de avaliação do artigo usa a **opção B** do enunciado: medir se a
verificação semântica funciona.

```bash
python avaliacao/gerar_corpus.py   # gera 52 programas
python avaliacao/medir.py          # imprime a tabela de resultados
python avaliacao/medir.py --detalhe
```

O corpus traz 42 programas com erro proposital, distribuídos pelos quatro grupos
de verificação, mais 10 programas corretos como controle. Seis dos casos são
limites conhecidos — erros que a verificação atual não alcança — e estão no
corpus de propósito, para que o número reportado não seja o número que
gostaríamos de ter.

## Decisões de implementação

**Parser escrito à mão, sem gerador.** Ganhamos controle total sobre a posição
de cada token, que é o que torna possível a mensagem de erro com linha, coluna e
cursor, e ganhamos palavras-chave contextuais (`por` e `a` só são palavra-chave
na posição em que o `passo` as espera, o que permite `preparo a { ... }`).
Perdemos a gramática declarativa: a EBNF de `docs/especificacao.md` e o código do
parser são dois artefatos que precisam ser mantidos em sincronia à mão.

**Escala no literal, não na saída.** O fator de porções é aplicado quando um
literal de família auto-escalável é lido. Com isso, `farinha = acucar * 1.5`
escala uma vez só e continua correto, e tempos e temperaturas ficam intactos sem
caso especial no gerador.

**Análise semântica e execução escritas pela equipe**, sem biblioteca, como
exige o enunciado.

## Divisão do trabalho

| Frente | Responsável |
|---|---|
| Gramática, EBNF e tabela de tokens | Gabriel Celestino, Leonardo Graças |
| Léxico e sintático | Alex Miller |
| Escopo e tabela de símbolos | Mariana Laines |
| Verificações semânticas | Leonardo Graças |
| Interpretador e geração de saída | Alex Miller, Gabriel Celestino |
| Corpus e coleta de dados da avaliação | Mariana Laines |
| Escrita do artigo | toda a equipe |

## Limitações conhecidas

- A verificação de valores impossíveis (VS4) só funciona quando a expressão é
  feita de literais. `seja a = 300 g; acucar = 200 g - a;` escapa.
- Conversão só dentro da família. `xic` e `g` não convertem entre si, porque
  isso exigiria densidade por ingrediente.
- `C` é a única unidade de temperatura. Fahrenheit exigiria conversão afim.
- Um ingrediente declarado e nunca usado não gera aviso.
- Um `passo` sem `por` conta como zero no tempo total, sem sinalizar.
- Não há operador unário: `-5 g` é erro de sintaxe, não quantidade negativa.

## Uso de inteligência artificial

A declaração de uso de ferramentas de IA, exigida pelo enunciado, está em
`docs/declaracao-ia.md` e deve ser preenchida pela equipe antes da entrega do
artigo.
