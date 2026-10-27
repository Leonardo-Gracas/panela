# Panela — especificação da linguagem

**Disciplina:** Projeto e Implementação de Compiladores · G00274.1 · 2026/2
**Equipe:** Alex Miller, Gabriel Celestino, Leonardo Graças, Mariana Laines

---

## 1. Propósito e público-alvo

Panela é uma linguagem de domínio específico para escrever receitas de cozinha
que podem ser recalculadas para qualquer número de porções sem erro de conta. O
público é quem precisa da mesma receita em escalas diferentes: blogs de
culinária que publicam a versão para quatro e para doze pessoas, cozinha
industrial que produz por lote variável, e quem simplesmente cozinha para um
número de pessoas que muda a cada semana.

O problema que a linguagem resolve é específico e conhecido de qualquer pessoa
que já dobrou uma receita: escalar não é multiplicar tudo. Dobrar a massa dobra
a farinha, mas não dobra a temperatura do forno, não dobra o tempo de forno de
forma linear, e produz "4,5 ovos" quando o ingrediente é contável. Uma planilha
multiplica tudo porque enxerga apenas números. Panela enxerga *quantidades*, com
família, e recusa as operações que a família não permite — antes de a receita
chegar à cozinha.

Uma biblioteca em Python resolveria a aritmética, mas não a notação: o autor da
receita continuaria escrevendo chamadas de função e lendo mensagens de erro de
runtime. A verificação que importa aqui é estática e orientada ao domínio, e é
isso que justifica uma linguagem própria em vez de uma API.

---

## 2. Programa de exemplo, comentado

```panela
receita "Bolo de cenoura" {          // abre a receita; o texto é o título da saída
  rende 12 porcoes;                  // escala de referência: tudo abaixo vale para 12

  ingrediente acucar   : massa;      // declaração global: nome + família do ingrediente
  ingrediente farinha  : massa;      // a família fixa que operações são legítimas
  ingrediente cenoura  : massa;
  ingrediente ovo      : contagem;   // contagem não aceita fração
  ingrediente oleo     : volume;
  ingrediente chocolate: massa;
  ingrediente leite    : volume;

  preparo massa {                    // abre um escopo próprio de nomes
    acucar  = 200 g;                 // liga o nome local 'acucar' ao ingrediente global
    farinha = acucar * 1.5;          // escala por número puro: proporção, não número mágico
    cenoura = 300 g;
    ovo     = 3 un;
    oleo    = 150 ml;

    passo "Bater cenoura, ovo e oleo no liquidificador" por 5 min;
    passo "Misturar farinha e acucar" por 4 min;
    passo "Assar" por 40 min a 180 C;   // 'por' exige tempo; 'a' exige temperatura
  }

  preparo cobertura {                // outro escopo: 'acucar' aqui é outro nome
    acucar    = 50 g;                // mesmo ingrediente global, valor local diferente
    chocolate = 100 g;
    leite     = 100 ml;

    passo "Derreter o chocolate com o leite" por 8 min;
    passo "Juntar o acucar e mexer" por 2 min;
  }

  montagem {                         // ordem de execução e cálculo do tempo total
    executar massa;
    executar cobertura;
  }
}
```

Compilado com `python -m panela exemplos/bolo.pan --porcoes 24`, o programa
produz a receita em Markdown com a lista de compras somada entre os dois
preparos (`acucar` aparece uma única vez, com 500 g), com massas e volumes
multiplicados por dois, e com os 40 min e os 180 C intactos.

---

## 3. Gramática (EBNF)

```ebnf
programa     = receita ;

receita      = "receita" CADEIA "{"
                 rendimento
                 { ingrediente }
                 { preparo }
                 montagem
               "}" ;

rendimento   = "rende" NUMERO "porcoes" ";" ;

ingrediente  = "ingrediente" IDENT ":" familia ";" ;
familia      = "massa" | "volume" | "contagem" | "tempo" | "temperatura" ;

preparo      = "preparo" IDENT "{" { comando } "}" ;
comando      = usa | local | passo ;
usa          = IDENT "=" expressao ";" ;
local        = "seja" IDENT "=" expressao ";" ;
passo        = "passo" CADEIA [ "por" expressao ] [ "a" expressao ] ";" ;

montagem     = "montagem" "{" { instrucao } "}" ;
instrucao    = executar | repeticao ;
executar     = "executar" IDENT ";" ;
repeticao    = "repetir" expressao "vezes" [ "em" ] modo
               "{" { instrucao } "}" ;
modo         = "sequencia" | "paralelo" ;

expressao    = termo { ( "+" | "-" ) termo } ;      (* nível 2: soma *)
termo        = fator { ( "*" | "/" ) fator } ;      (* nível 1: escala *)
fator        = quantidade
             | NUMERO
             | IDENT
             | "(" expressao ")" ;

quantidade   = NUMERO UNIDADE ;

IDENT        = letra { letra | digito | "_" } ;
NUMERO       = digito { digito } [ "." digito { digito } ] ;
CADEIA       = '"' { caractere } '"' ;
UNIDADE      = "g" | "kg" | "ml" | "l" | "xic" | "cs" | "cc"
             | "un" | "min" | "h" | "C" ;
```

Dois níveis de precedência: `*` e `/` ligam mais forte que `+` e `-`, e o
parêntese devolve o controle ao nível de cima. `200 g + 50 g * 3` vale 350 g;
`(200 g + 50 g) * 3` vale 750 g.

---

## 4. Tabela de tokens

| Token | Lexema | Observação |
|---|---|---|
| `RECEITA` | `receita` | abre a unidade de compilação |
| `RENDE` / `PORCOES` | `rende`, `porcoes` | escala de referência |
| `INGREDIENTE` | `ingrediente` | declaração global de identidade |
| `PREPARO` | `preparo` | abre um escopo de nomes |
| `SEJA` | `seja` | nome auxiliar, não vai à lista de compras |
| `PASSO` | `passo` | instrução textual com tempo e temperatura opcionais |
| `MONTAGEM` | `montagem` | ordem de execução |
| `EXECUTAR` | `executar` | invoca um preparo |
| `REPETIR` / `VEZES` / `EM` | `repetir`, `vezes`, `em` | repetição do domínio |
| `SEQUENCIA` / `PARALELO` | `sequencia`, `paralelo` | decide se o tempo soma |
| `FAMILIA` | `massa`, `volume`, `contagem`, `tempo`, `temperatura` | também aceito como nome comum |
| `UNIDADE` | `g kg ml l xic cs cc un min h C` | define a família do literal |
| `IDENT` | `farinha`, `massa_pronta` | letra inicial, depois letras, dígitos e `_` |
| `NUMERO` | `200`, `1.5` | decimal com ponto |
| `CADEIA` | `"Assar"` | entre aspas, sem quebra de linha |
| `IGUAL` | `=` | ligação de nome |
| `MAIS` `MENOS` | `+` `-` | precedência 2 |
| `VEZES_OP` `BARRA` | `*` `/` | precedência 1 |
| `ABRE_PAR` `FECHA_PAR` | `(` `)` | agrupamento |
| `ABRE_CHAVE` `FECHA_CHAVE` | `{` `}` | blocos |
| `PONTO_VIRGULA` `DOIS_PONTOS` `VIRGULA` | `;` `:` `,` | pontuação |
| `FIM` | — | fim do arquivo |

Comentários `// linha` e `/* bloco */` são descartados pelo léxico.

`por` e `a` são **palavras-chave contextuais**: valem como palavra-chave apenas
na posição em que o `passo` as espera, e em qualquer outro lugar são nomes
comuns. Isso permite escrever `preparo a { ... }` sem conflito com
`passo "assar" a 180 C`.

---

## 5. Verificações semânticas

O compilador roda quatro verificações, todas estáticas e todas anteriores à
execução. As três primeiras são as verificações centrais do domínio; a quarta
cobre valores que são sintaticamente válidos e impossíveis na cozinha.

| Grupo | O que verifica | Códigos |
|---|---|---|
| **VS1 — coerência de família** | só se soma o que pertence à mesma família; `por` exige tempo, `a` exige temperatura; o ingrediente recebe a família com que foi declarado | `PAN-F01` a `PAN-F05` |
| **VS2 — operação própria da família** | temperatura não soma nem escala; quantidade não multiplica quantidade; repetição exige número puro | `PAN-O01` a `PAN-O05` |
| **VS3 — nomes e identidade** | todo nome usado existe no escopo em que aparece; nada é declarado duas vezes; `executar` aponta para um preparo que existe | `PAN-E01` a `PAN-E06` |
| **VS4 — valores impossíveis** | quantidade negativa ou zero, fração em contagem, divisão por zero, repetição fracionária (por dobra de constantes) | `PAN-C01` a `PAN-C04` |

### Programa que passa

```panela
receita "Calda" {
  rende 4 porcoes;
  ingrediente acucar : massa;
  ingrediente agua   : volume;

  preparo calda {
    acucar = 200 g + 50 g * 3;    // 350 g — precedência correta
    agua   = 100 ml;
    passo "Ferver" por 10 min a 110 C;
  }

  montagem { executar calda; }
}
```

### Programa que é rejeitado

```panela
receita "Calda" {
  rende 4 porcoes;
  ingrediente acucar : massa;

  preparo calda {
    acucar = 200 g + 30 min;      // soma massa com tempo
    passo "Ferver" por 10 min;
  }

  montagem { executar calda; }
}
```

Mensagem pretendida, e efetivamente produzida pelo compilador:

```
calda.pan:6:20: erro PAN-F01: nao da para somar massa com tempo
     6 |     acucar = 200 g + 30 min;
       |                     ^
  dica: so quantidades da mesma familia podem ser somadas
```

A linha está sintaticamente perfeita. É a verificação semântica que a recusa, e
a mensagem traz arquivo, linha e coluna, com o trecho e o cursor sob o operador
culpado.

---

## 6. Três construções consideradas e descartadas

**Conversão entre famílias por densidade.** Converter `200 g` de açúcar em
xícaras é possível, mas exige uma tabela de densidade por ingrediente — açúcar,
farinha e cacau ocupam volumes diferentes para a mesma massa. Isso move o
projeto de "compilador" para "base de dados de alimentos", e a qualidade do
resultado passa a depender da tabela, não da linguagem. Descartado: a conversão
em Panela acontece apenas *dentro* da família (`g ↔ kg`, `ml ↔ l ↔ xic`,
`min ↔ h`), onde o fator é exato e universal.

**Escala não-linear de tempo.** O tempo de forno não é proporcional à massa: o
dobro de bolo não assa em o dobro do tempo, e a relação real depende de
geometria, condução e tipo de forno. Modelar isso corretamente é problema de
engenharia de alimentos, e modelar errado seria pior do que não modelar.
Descartado: tempo é somável e escalável quando o autor escreve a conta, mas a
escala automática por porções não o toca, e a saída diz isso explicitamente ao
leitor.

**Preparos com parâmetros.** Era tentador escrever `preparo massa(fator)` e
reaproveitar o mesmo bloco com valores diferentes. Isso é, na prática, função
definida pelo usuário, item que o enunciado coloca fora do escopo desta versão —
e traria junto passagem de argumentos, verificação de aridade e escopo aninhado.
Descartado: a mesma necessidade é atendida por `repetir N vezes`, que multiplica
o consumo sem introduzir chamada de função.

---

## 7. Fora do escopo desta versão

Não há funções definidas pelo usuário, recursão, inferência de tipos, closures,
módulos ou tratamento de exceções. Não há condicional: uma receita em Panela é
determinística. Não há operador unário de negação, porque quantidade negativa
não tem sentido no domínio — o que torna `a - b` a única forma de chegar a um
valor negativo, e é exatamente isso que `PAN-C02` recusa.
