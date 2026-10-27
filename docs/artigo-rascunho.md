# Panela: uma linguagem de domínio específico para receitas que escalam

> **Rascunho para a equipe.** Este arquivo traz a estrutura exigida pelo
> enunciado, os dados realmente medidos e o argumento de cada seção. A equipe
> deve reescrever o texto com as próprias palavras antes de levar para o
> template ACM sigconf, completar as referências e preencher a declaração de uso
> de IA. A arguição da apresentação é individual e pergunta sobre decisões do
> código: quem apresentar precisa ter lido a implementação.

**Equipe:** Alex Miller, Gabriel Celestino, Leonardo Graças, Mariana Laines
**Repositório:** _inserir URL_

---

## Resumo

_A escrever ao final, em 150–200 palavras: domínio, o que a linguagem faz, qual
verificação semântica foi implementada, e o resultado principal da avaliação
(37 de 42 programas com erro proposital recusados, nenhum falso positivo em 10
programas de controle)._

---

## 1. Introdução

**O domínio.** Receitas de cozinha publicadas em escala fixa precisam ser
recalculadas para outro número de porções. Quem faz isso à mão, ou com planilha,
multiplica todos os números pelo mesmo fator.

**O problema.** Escalar uma receita não é multiplicar tudo. Multiplicar a massa
de farinha por dois está correto; multiplicar a temperatura do forno por dois
não significa nada; multiplicar o tempo de forno por dois está errado por razões
de física, não de aritmética; e multiplicar três ovos por 1,5 produz um valor
que não existe no mundo. O erro não está na multiplicação, está em multiplicar o
que não devia — e nenhuma dessas quatro operações é distinguível das outras
quando o programa enxerga apenas números.

**Por que uma linguagem e não uma biblioteca.** Uma biblioteca em Python
resolveria a aritmética com um tipo `Quantidade` e sobrecarga de operadores. O
que ela não resolve é o momento da verificação e a forma da notação. Em
biblioteca, `200 * g + 30 * min` só falha quando a linha executa, com uma
exceção de runtime e um *traceback* que fala de classes, não de ingredientes. Em
Panela, essa linha é recusada pela análise semântica, antes de qualquer
execução, com arquivo, linha, coluna e uma mensagem escrita no vocabulário de
quem cozinha. A verificação que importa neste domínio é estática, e verificação
estática sobre notação própria é exatamente o que caracteriza uma linguagem.

**Contribuição.** Apresentamos Panela: a linguagem, a implementação completa
(léxico, sintático, semântico e execução, escritos pela equipe) e uma avaliação
quantitativa da eficácia da verificação semântica sobre um corpus de 52
programas.

_Citar aqui a bibliografia da disciplina sobre análise semântica e sobre DSLs._

---

## 2. A linguagem

### 2.1 Programa de exemplo

_Inserir o bolo de cenoura de `docs/especificacao.md`, reduzido a meia coluna, e
mostrar a saída em Markdown ao lado, para 12 e para 24 porções._

### 2.2 Construções principais

**Quantidade com família.** O tipo central não é número: é quantidade, composta
de valor, unidade e família. São cinco famílias — massa, volume, contagem, tempo
e temperatura — e cada uma carrega duas propriedades que a análise semântica
consulta: se é somável e se é escalável. Temperatura é a única não somável e não
escalável, porque é um ponto numa escala e não uma grandeza que se acumula.

**Escopo por preparo.** Cada bloco `preparo` abre um escopo de nomes. Dois
preparos podem ter cada um o seu `acucar` sem colisão. A identidade do
ingrediente, porém, é global, declarada uma única vez com `ingrediente`, e é
isso que permite somar os dois em uma única linha da lista de compras.

**Repetição com modo.** `repetir N vezes em sequencia` multiplica ingredientes e
tempo; `em paralelo` multiplica apenas os ingredientes. Três camadas no mesmo
forno gastam três vezes a massa e assam uma vez só.

### 2.3 Três decisões de projeto

**Decisão 1 — conversão só dentro da família.** `g ↔ kg` e `ml ↔ l ↔ xic`
convertem; `g ↔ xic` não. *Alternativa descartada:* uma tabela de densidade por
ingrediente, que permitiria converter massa em volume. *Motivo:* a correção do
resultado passaria a depender da qualidade da tabela de alimentos, não da
linguagem, e o projeto migraria de compilador para base de dados. O custo da
decisão é real e aparece na avaliação: uma receita que mistura `xic` e `g` para
o mesmo ingrediente é recusada, embora fosse legítima na cozinha.

**Decisão 2 — escala aplicada no literal, não na saída.** O fator de porções é
aplicado no momento em que um literal de família auto-escalável é lido pelo
interpretador. *Alternativa descartada:* escalar as quantidades finais no
gerador de saída. *Motivo:* com a escala no literal, expressões derivadas como
`farinha = acucar * 1.5` escalam uma vez só e permanecem corretas, e tempo e
temperatura ficam intactos sem nenhum caso especial no gerador. A regra "o que
escala é a família, não o resultado" fica concentrada em um ponto do código.

**Decisão 3 — parser de descida recursiva escrito à mão.** *Alternativa
descartada:* Lark. *Motivo:* o enunciado exige mensagens com arquivo, linha e
coluna, e escrever o léxico à mão deu controle total sobre a posição de cada
token, inclusive para apontar o operador exato em `200 g + 30 min`. O parser à
mão também viabilizou palavras-chave contextuais: `por` e `a` são palavra-chave
apenas na posição em que o comando `passo` as espera, o que permite escrever
`preparo a { ... }` sem ambiguidade — algo que exigiria contorção em uma
gramática declarativa. *O que se perdeu:* a EBNF da especificação e o código do
parser são dois artefatos mantidos em sincronia à mão, e qualquer mudança na
gramática precisa ser feita duas vezes.

---

## 3. Implementação

Python 3.12, sem dependências de execução. 1.321 linhas de código em oito
módulos (`wc -l panela/*.py`), mais 35 testes automatizados.

**Análise léxica** (`lexer.py`). Varredura caractere a caractere, mantendo
linha e coluna em cada avanço. Toda unidade reconhecida vira token `UNIDADE`, o
que resolve no léxico a distinção entre `g` como unidade e um nome qualquer.
*Dificuldade:* a palavra-chave `a`, natural em "assar por 40 min **a** 180 C",
colidia com qualquer preparo chamado `a`. *Solução:* `por` e `a` deixaram de ser
reservadas e passaram a ser reconhecidas pelo parser apenas na posição esperada.

**Análise sintática** (`parser.py`). Descida recursiva com dois níveis de
precedência: `expressao` trata `+` e `-`, `termo` trata `*` e `/`, e o parêntese
retorna ao nível superior. *Dificuldade:* mensagens de erro úteis quando falta
`;`. *Solução:* cada chamada a `_exigir` recebe uma descrição do contexto, e a
mensagem aponta o token encontrado, não um símbolo da gramática.

**Análise semântica** (`semantica.py`). Um percurso da árvore que infere, para
cada expressão, se ela é número puro ou quantidade de uma família. O escopo é
um dicionário reiniciado a cada `preparo`. *Dificuldade:* decidir onde a
identidade global do ingrediente convive com o nome local. *Solução:* duas
tabelas separadas — ingredientes da receita e nomes do preparo corrente — e a
atribuição exige que o nome exista na primeira.

**Execução** (`interpretador.py`). Avalia cada preparo uma vez, depois percorre
a montagem contando execuções, acumulando a lista de compras e somando o tempo
conforme o modo da repetição. *Dificuldade:* arredondamento de contagem.
*Solução:* arredondamento para cima no momento da compra, documentado na saída.

---

## 4. Avaliação

Adotamos a **opção B** do enunciado: medir se a verificação semântica funciona.

### 4.1 Método

Construímos um corpus de 52 programas: 42 com erro proposital e 10 corretos como
controle. Cada arquivo declara em seu cabeçalho o código de erro que a
verificação deveria apontar, e um script (`avaliacao/medir.py`) compila todos,
compara o código obtido com o declarado e classifica cada caso em detectado,
escapou ou falso positivo.

Os 42 casos com erro cobrem os quatro grupos de verificação. Seis deles foram
escritos deliberadamente **fora** do alcance conhecido da implementação, para
que o número reportado não fosse apenas o número que esperávamos.

### 4.2 Resultados

| Categoria | Casos | Detectados | Escaparam | Falsos positivos | Taxa |
|---|---|---|---|---|---|
| VS1 — coerência de família | 10 | 10 | 0 | 0 | 100% |
| VS2 — operação própria da família | 10 | 10 | 0 | 0 | 100% |
| VS3 — nomes e identidade | 10 | 10 | 0 | 0 | 100% |
| VS4 — valores impossíveis | 6 | 6 | 0 | 0 | 100% |
| Limites conhecidos | 6 | 1 | 5 | 0 | 17% |
| Controle (programas corretos) | 10 | — | — | 0 | 100% sem alarme falso |
| **Total** | **52** | **37** | **5** | **0** | — |

Um caso merece nota: `lim_06`, em que um ingrediente declarado como massa recebe
`1 xic`, foi detectado, mas com um código diferente do previsto — a verificação
de família do ingrediente (`PAN-F05`) o pegou antes que a ausência de conversão
entre famílias se manifestasse. É uma detecção correta por um caminho que não
havíamos antecipado.

### 4.3 Interpretação

Os 100% nos quatro grupos implementados dizem menos do que parecem. O corpus foi
escrito pelas mesmas pessoas que escreveram o verificador, e um teste construído
por quem conhece a implementação tende a testar exatamente o que ela trata. O
número que informa de verdade é o da categoria "limites conhecidos": cinco
escapes em seis tentativas de burlar a verificação por caminhos que sabíamos
frágeis. A fronteira da verificação é a avaliação constante das expressões — ela
pega `200 g - 300 g`, mas não pega a mesma conta quando o 300 g chega por um
nome.

A ausência de falsos positivos nos 10 controles é o resultado mais confiável do
conjunto, porque falso positivo é o erro que mais atrapalha quem usa a
linguagem: um verificador que recusa receitas corretas é abandonado na primeira
semana.

**O que estes números não permitem concluir.** Não permitem afirmar que a
verificação pega os erros que *usuários reais* cometeriam — para isso seria
preciso coletar receitas escritas por terceiros, que é a opção C do enunciado.
Não permitem comparar com outra ferramenta, porque não há linha de base. E não
medem usabilidade das mensagens de erro: medimos se o erro é detectado, não se a
mensagem ajuda a corrigi-lo.

---

## 5. Limitações

**Verificação de valores depende de constantes.** VS4 dobra expressões feitas só
de literais. `seja a = 300 g; acucar = 200 g - a;` passa pela análise e produz
uma quantidade negativa na saída. *Causa:* não implementamos propagação de
constantes por nomes; seria necessário um passe adicional de análise de fluxo.

**Sem conversão entre famílias.** `xic` e `g` não convertem entre si. *Causa:*
decisão de projeto deliberada (seção 2.3), para não depender de tabela de
densidade por ingrediente.

**Temperatura só em Celsius.** *Causa:* Fahrenheit exigiria conversão afim, com
deslocamento além do fator, e o modelo de quantidade guarda apenas um fator
multiplicativo para a unidade base.

**Escala de tempo é tudo ou nada.** A escala automática por porções não toca o
tempo. *Causa:* a relação real entre massa e tempo de cocção não é linear e
depende de variáveis fora do alcance do programa. Preferimos não escalar a
escalar errado, e a saída informa isso ao leitor.

**Passo sem duração não é sinalizado.** Um `passo` sem `por` conta como zero no
tempo total, silenciosamente. *Causa:* não distinguimos "passo instantâneo" de
"duração esquecida".

**Ingrediente declarado e nunca usado não gera aviso.** *Causa:* implementamos o
aviso equivalente para preparos e não estendemos a ingredientes.

---

## 6. Conclusão

Panela mostra que uma linguagem pequena — cinco famílias de quantidade, dois
níveis de precedência, um bloco de escopo e uma forma de repetição — é
suficiente para capturar um erro que planilhas e calculadoras cometem todos os
dias. A escolha de projeto que sustenta todo o resto é tratar quantidade, e não
número, como tipo central: uma vez que a família faz parte do tipo, as
verificações deixam de ser casos especiais e passam a ser consequência da
álgebra de cada família.

O trabalho futuro mais evidente é fechar a fronteira que a avaliação expôs:
propagar constantes por nomes, de modo que a verificação de valores impossíveis
alcance expressões indiretas.

---

## Declaração de uso de inteligência artificial

_Ver `docs/declaracao-ia.md`. **Obrigatório preencher.**_

## Referências

_Mínimo de 5, com pelo menos 2 da bibliografia da disciplina. Sugestões de
categoria a cobrir: (i) livro-texto de compiladores da disciplina, para análise
semântica e tabela de símbolos; (ii) referência sobre linguagens de domínio
específico e quando elas se justificam frente a bibliotecas; (iii) trabalho
sobre sistemas de tipos com unidades de medida; (iv) referência sobre análise de
fluxo/propagação de constantes, citada nas limitações; (v) documentação ou
artigo sobre a técnica de descida recursiva._
