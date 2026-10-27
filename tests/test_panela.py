"""Testes automatizados da linguagem Panela."""

import pytest

from panela.cli import compilar
from panela.erros import ErroLexico, ErroSemantico, ErroSintatico
from panela.interpretador import gerar_markdown
from panela.lexer import tokenizar
from panela.parser import analisar
from panela.quantidade import Quantidade, formatar, formatar_tempo

BASE = """receita "T" {{
  rende 2 porcoes;
  ingrediente acucar : massa;
  preparo p {{
    {corpo}
  }}
  montagem {{
    executar p;
  }}
}}"""


def fonte(corpo):
    return BASE.format(corpo=corpo)


def compila(corpo):
    return compilar(fonte(corpo), "t.pan")[0]


def erro(corpo):
    with pytest.raises(ErroSemantico) as e:
        compilar(fonte(corpo), "t.pan")
    return e.value


# ----------------------------------------------------------------- lexico
def test_lexer_classifica_unidade_e_familia():
    tipos = [t.tipo for t in tokenizar("200 g massa acucar", "t.pan")]
    assert tipos == ["NUMERO", "UNIDADE", "FAMILIA", "IDENT", "FIM"]


def test_lexer_guarda_linha_e_coluna():
    tok = tokenizar("\n  200 g", "t.pan")[0]
    assert (tok.pos.linha, tok.pos.coluna) == (2, 3)


def test_lexer_ignora_comentarios():
    tipos = [t.tipo for t in tokenizar("// nada\n/* nada */ 5", "t.pan")]
    assert tipos == ["NUMERO", "FIM"]


def test_lexer_rejeita_texto_sem_fechar():
    with pytest.raises(ErroLexico) as e:
        tokenizar('passo "sem fim;', "t.pan")
    assert e.value.codigo == "PAN-L02"


# ---------------------------------------------------------------- sintaxe
def test_parser_monta_a_receita():
    r = analisar(fonte("acucar = 200 g;"), "t.pan")
    assert r.titulo == "T"
    assert r.rende == 2
    assert r.preparos[0].nome == "p"


def test_precedencia_multiplicacao_antes_de_soma():
    r = analisar(fonte("acucar = 200 g + 50 g * 3;"), "t.pan")
    topo = r.preparos[0].comandos[0].expr
    assert topo.op == "+"
    assert topo.dir.op == "*"


def test_parentese_inverte_a_precedencia():
    r = analisar(fonte("acucar = (200 g + 50 g) * 3;"), "t.pan")
    topo = r.preparos[0].comandos[0].expr
    assert topo.op == "*"
    assert topo.esq.op == "+"


def test_erro_de_sintaxe_tem_posicao():
    with pytest.raises(ErroSintatico) as e:
        analisar(fonte("acucar = 200 g"), "t.pan")
    assert e.value.linha == 6   # aponta o token onde o ponto e virgula faltou


def test_repeticao_exige_modo():
    corpo = """receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      preparo p { acucar = 1 g; }
      montagem { repetir 2 vezes { executar p; } }
    }"""
    with pytest.raises(ErroSintatico) as e:
        analisar(corpo, "t.pan")
    assert e.value.codigo == "PAN-S04"


# ------------------------------------------- VS1: coerencia de familia
def test_vs1_soma_de_familias_diferentes():
    assert erro("acucar = 200 g + 30 min;").codigo == "PAN-F01"


def test_vs1_quantidade_com_numero_puro():
    assert erro("acucar = 200 g + 5;").codigo == "PAN-F02"


def test_vs1_ingrediente_recebe_familia_errada():
    assert erro("acucar = 200 ml;").codigo == "PAN-F05"


def test_vs1_duracao_precisa_ser_tempo():
    assert erro('acucar = 1 g; passo "x" por 200 g;').codigo == "PAN-F03"


def test_vs1_temperatura_precisa_ser_temperatura():
    assert erro('acucar = 1 g; passo "x" a 30 min;').codigo == "PAN-F04"


def test_vs1_aceita_soma_da_mesma_familia():
    compila("acucar = 200 g + 1 kg;")


# -------------------------------------------- VS2: operacao da familia
def test_vs2_temperatura_nao_soma():
    assert erro('acucar = 1 g; passo "x" a 180 C + 20 C;').codigo == "PAN-O01"


def test_vs2_temperatura_nao_escala():
    assert erro('acucar = 1 g; passo "x" a 180 C * 2;').codigo == "PAN-O02"


def test_vs2_quantidade_vezes_quantidade():
    assert erro("acucar = 200 g * 2 g;").codigo == "PAN-O03"


def test_vs2_numero_dividido_por_quantidade():
    assert erro("acucar = 2 / 200 g;").codigo == "PAN-O04"


def test_vs2_divisao_da_mesma_familia_vira_numero():
    compila("seja razao = 400 g / 200 g; acucar = 100 g * razao;")


def test_vs2_repeticao_precisa_de_numero_puro():
    programa = """receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      preparo p { acucar = 1 g; }
      montagem { repetir 2 min vezes em sequencia { executar p; } }
    }"""
    with pytest.raises(ErroSemantico) as e:
        compilar(programa, "t.pan")
    assert e.value.codigo == "PAN-O05"


# ------------------------------------------------ VS3: nomes e escopo
def test_vs3_nome_nao_declarado():
    assert erro("acucar = base * 2;").codigo == "PAN-E01"


def test_vs3_ingrediente_nao_declarado():
    assert erro("sal = 5 g;").codigo == "PAN-E04"


def test_vs3_preparo_inexistente():
    programa = """receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      preparo p { acucar = 1 g; }
      montagem { executar outro; }
    }"""
    with pytest.raises(ErroSemantico) as e:
        compilar(programa, "t.pan")
    assert e.value.codigo == "PAN-E03"


def test_vs3_nome_duplicado():
    assert erro("acucar = 1 g; acucar = 2 g;").codigo == "PAN-E02"


def test_vs3_escopo_e_local_ao_preparo():
    programa = """receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      ingrediente sal : massa;
      preparo a { seja base = 10 g; acucar = base; }
      preparo b { sal = base; }
      montagem { executar a; executar b; }
    }"""
    with pytest.raises(ErroSemantico) as e:
        compilar(programa, "t.pan")
    assert e.value.codigo == "PAN-E01"


def test_vs3_erro_carrega_arquivo_linha_e_coluna():
    e = erro("acucar = 200 g + 30 min;")
    assert e.arquivo == "t.pan"
    assert e.linha == 5
    assert e.coluna > 0
    assert "t.pan:5:" in e.cabecalho()


# --------------------------------------------------------- quantidades
def test_conversao_dentro_da_familia():
    assert Quantidade.de_literal(1, "kg").valor == 1000
    assert Quantidade.de_literal(1, "xic").valor == 240
    assert Quantidade.de_literal(2, "h").valor == 120


def test_formatacao_escolhe_a_unidade_legivel():
    assert formatar(Quantidade(1500, "massa")) == "1,5 kg"
    assert formatar(Quantidade(250, "massa")) == "250 g"
    assert formatar_tempo(85) == "1 h 25 min"


def test_contagem_arredonda_para_cima():
    r = compilar("""receita "T" {
      rende 2 porcoes;
      ingrediente ovo : contagem;
      preparo p { ovo = 3 un; }
      montagem { executar p; }
    }""", "t.pan")[0]
    md = gerar_markdown(r, porcoes=3)       # fator 1,5 -> 4,5 ovos
    assert "ovo** — 5 un" in md


# ------------------------------------------------------------ execucao
def test_escala_mexe_em_massa_e_nao_em_tempo():
    r = compilar("""receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      preparo p { acucar = 100 g; passo "assar" por 30 min a 180 C; }
      montagem { executar p; }
    }""", "t.pan")[0]
    md = gerar_markdown(r, porcoes=4)
    assert "acucar** — 200 g" in md
    assert "30 min" in md
    assert "180 C" in md


def test_lista_de_compras_soma_entre_preparos():
    r = compilar("""receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      preparo a { acucar = 200 g; }
      preparo b { acucar = 50 g; }
      montagem { executar a; executar b; }
    }""", "t.pan")[0]
    assert "acucar** — 250 g" in gerar_markdown(r)


def test_repeticao_em_sequencia_soma_o_tempo():
    r = compilar("""receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      preparo p { acucar = 10 g; passo "fritar" por 10 min; }
      montagem { repetir 3 vezes em sequencia { executar p; } }
    }""", "t.pan")[0]
    md = gerar_markdown(r)
    assert "Tempo total:** 30 min" in md
    assert "acucar** — 30 g" in md


def test_repeticao_em_paralelo_nao_soma_o_tempo():
    r = compilar("""receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      preparo p { acucar = 10 g; passo "assar" por 10 min; }
      montagem { repetir 3 vezes em paralelo { executar p; } }
    }""", "t.pan")[0]
    md = gerar_markdown(r)
    assert "Tempo total:** 10 min" in md
    assert "acucar** — 30 g" in md        # ingrediente multiplica mesmo assim


def test_preparo_nunca_executado_gera_aviso():
    avisos = compilar("""receita "T" {
      rende 2 porcoes;
      ingrediente acucar : massa;
      ingrediente sal : massa;
      preparo a { acucar = 1 g; }
      preparo b { sal = 1 g; }
      montagem { executar a; }
    }""", "t.pan")[1]
    assert any("'b'" in x for x in avisos)
