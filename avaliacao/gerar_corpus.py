"""Gera o corpus da avaliacao (opcao B do enunciado).

Cada caso declara, no proprio arquivo, o codigo de erro que a verificacao
deveria apontar -- ou ERRO: nenhum, para os programas de controle. O runner
compara essa expectativa com o que o compilador de fato faz.
"""

import os
import textwrap

AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(AQUI, "corpus")


def receita(corpo_preparo, extras="", rende=4, montagem="executar p;",
            ingredientes="ingrediente acucar : massa;"):
    return textwrap.dedent(f"""\
        receita "Caso de teste" {{
          rende {rende} porcoes;

          {ingredientes}
        {extras}
          preparo p {{
        {textwrap.indent(textwrap.dedent(corpo_preparo).strip(), "    ")}
          }}

          montagem {{
            {montagem}
          }}
        }}
        """)


# (arquivo, codigo esperado ou None, categoria, fonte)
CASOS = []


def caso(nome, esperado, categoria, fonte):
    CASOS.append((nome, esperado, categoria, fonte))


# ------------------------------------------------ VS1 coerencia de familia
caso("vs1_01_massa_mais_tempo", "PAN-F01", "VS1",
     receita('acucar = 200 g + 30 min;\npasso "x" por 5 min;'))
caso("vs1_02_massa_mais_volume", "PAN-F01", "VS1",
     receita('acucar = 200 g + 100 ml;\npasso "x" por 5 min;'))
caso("vs1_03_volume_menos_massa", "PAN-F01", "VS1",
     receita('agua = 500 ml - 100 g;\npasso "x" por 5 min;',
             ingredientes="ingrediente agua : volume;"))
caso("vs1_04_contagem_mais_massa", "PAN-F01", "VS1",
     receita('ovo = 2 un + 50 g;\npasso "x" por 5 min;',
             ingredientes="ingrediente ovo : contagem;"))
caso("vs1_05_quantidade_mais_numero", "PAN-F02", "VS1",
     receita('acucar = 200 g + 5;\npasso "x" por 5 min;'))
caso("vs1_06_ingrediente_familia_errada", "PAN-F05", "VS1",
     receita('acucar = 250 ml;\npasso "x" por 5 min;'))
caso("vs1_07_duracao_em_massa", "PAN-F03", "VS1",
     receita('acucar = 200 g;\npasso "x" por 200 g;'))
caso("vs1_08_temperatura_em_tempo", "PAN-F04", "VS1",
     receita('acucar = 200 g;\npasso "x" por 10 min a 30 min;'))
caso("vs1_09_divisao_entre_familias", "PAN-F01", "VS1",
     receita('seja r = 200 g / 10 min;\nacucar = 100 g * r;\npasso "x" por 5 min;'))
caso("vs1_10_soma_via_nome_local", "PAN-F01", "VS1",
     receita('seja t = 30 min;\nacucar = 200 g + t;\npasso "x" por 5 min;'))

# ------------------------------------------- VS2 operacao propria da familia
caso("vs2_01_temperatura_somada", "PAN-O01", "VS2",
     receita('acucar = 200 g;\npasso "x" por 10 min a 180 C + 20 C;'))
caso("vs2_02_temperatura_escalada", "PAN-O02", "VS2",
     receita('acucar = 200 g;\npasso "x" por 10 min a 180 C * 2;'))
caso("vs2_03_temperatura_dividida", "PAN-O02", "VS2",
     receita('acucar = 200 g;\npasso "x" por 10 min a 180 C / 2;'))
caso("vs2_04_massa_vezes_massa", "PAN-O03", "VS2",
     receita('acucar = 200 g * 2 g;\npasso "x" por 5 min;'))
caso("vs2_05_volume_vezes_tempo", "PAN-O03", "VS2",
     receita('agua = 100 ml * 2 min;\npasso "x" por 5 min;',
             ingredientes="ingrediente agua : volume;"))
caso("vs2_06_numero_dividido_por_quantidade", "PAN-O04", "VS2",
     receita('acucar = 2 / 200 g;\npasso "x" por 5 min;'))
caso("vs2_07_repeticao_com_quantidade", "PAN-O05", "VS2",
     receita('acucar = 200 g;\npasso "x" por 5 min;',
             montagem="repetir 3 min vezes em sequencia { executar p; }"))
caso("vs2_08_temperatura_somada_via_nome", "PAN-O01", "VS2",
     receita('seja forno = 180 C;\nacucar = 200 g;\n'
             'passo "x" por 10 min a forno + 10 C;'))
caso("vs2_09_temperatura_escalada_via_nome", "PAN-O02", "VS2",
     receita('seja forno = 180 C;\nacucar = 200 g;\n'
             'passo "x" por 10 min a forno * 1.5;'))
caso("vs2_10_quantidade_vezes_quantidade_em_parenteses", "PAN-O03", "VS2",
     receita('acucar = (100 g + 100 g) * (2 g);\npasso "x" por 5 min;'))

# ---------------------------------------------------- VS3 nomes e identidade
caso("vs3_01_nome_inexistente", "PAN-E01", "VS3",
     receita('acucar = base * 2;\npasso "x" por 5 min;'))
caso("vs3_02_local_de_outro_preparo", "PAN-E01", "VS3",
     receita('sal = base;\npasso "x" por 5 min;',
             ingredientes="ingrediente acucar : massa;\n  ingrediente sal : massa;",
             extras="  preparo q {\n    seja base = 10 g;\n    acucar = base;\n  }\n",
             montagem="executar q;\n    executar p;"))
caso("vs3_03_ingrediente_nao_declarado", "PAN-E04", "VS3",
     receita('sal = 5 g;\npasso "x" por 5 min;'))
caso("vs3_04_ingrediente_duplicado", "PAN-E02", "VS3",
     receita('acucar = 200 g;\npasso "x" por 5 min;',
             ingredientes="ingrediente acucar : massa;\n  "
                          "ingrediente acucar : volume;"))
caso("vs3_05_valor_atribuido_duas_vezes", "PAN-E02", "VS3",
     receita('acucar = 200 g;\nacucar = 50 g;\npasso "x" por 5 min;'))
caso("vs3_06_preparo_inexistente", "PAN-E03", "VS3",
     receita('acucar = 200 g;\npasso "x" por 5 min;',
             montagem="executar outro;"))
caso("vs3_07_preparo_duplicado", "PAN-E02", "VS3",
     receita('acucar = 200 g;\npasso "x" por 5 min;',
             extras="  preparo p {\n    acucar = 10 g;\n  }\n"))
caso("vs3_08_ingrediente_usado_antes_do_valor", "PAN-E01", "VS3",
     receita('seja dobro = acucar * 2;\nacucar = 200 g;\npasso "x" por 5 min;'))
caso("vs3_09_nome_local_dentro_de_repeticao", "PAN-E03", "VS3",
     receita('acucar = 200 g;\npasso "x" por 5 min;',
             montagem="repetir 2 vezes em sequencia { executar q; }"))
caso("vs3_10_rende_zero", "PAN-E06", "VS3",
     receita('acucar = 200 g;\npasso "x" por 5 min;', rende=0))

# ----------------------------------------------------------- controles (ok)
caso("ok_01_basico", None, "controle",
     receita('acucar = 200 g;\npasso "x" por 5 min;'))
caso("ok_02_soma_mesma_familia", None, "controle",
     receita('acucar = 200 g + 1 kg;\npasso "x" por 5 min;'))
caso("ok_03_escala_por_numero", None, "controle",
     receita('acucar = 200 g * 3;\npasso "x" por 5 min;'))
caso("ok_04_proporcao_entre_quantidades", None, "controle",
     receita('seja r = 400 g / 200 g;\nacucar = 100 g * r;\npasso "x" por 5 min;'))
caso("ok_05_precedencia", None, "controle",
     receita('acucar = 200 g + 50 g * 3;\npasso "x" por 5 min;'))
caso("ok_06_parenteses", None, "controle",
     receita('acucar = (200 g + 50 g) * 3;\npasso "x" por 5 min;'))
caso("ok_07_tempo_somado", None, "controle",
     receita('acucar = 200 g;\npasso "x" por 30 min + 15 min;'))
caso("ok_08_temperatura_simples", None, "controle",
     receita('acucar = 200 g;\npasso "x" por 40 min a 180 C;'))
caso("ok_09_dois_preparos_mesmo_nome_local", None, "controle",
     receita('acucar = 50 g;\npasso "x" por 5 min;',
             ingredientes="ingrediente acucar : massa;\n  ingrediente sal : massa;",
             extras="  preparo q {\n    acucar = 200 g;\n    sal = 5 g;\n  }\n",
             montagem="executar q;\n    executar p;"))
caso("ok_10_repeticoes", None, "controle",
     receita('acucar = 100 g;\npasso "x" por 10 min;',
             montagem="repetir 2 vezes em sequencia { executar p; }\n"
                      "    repetir 3 vezes em paralelo { executar p; }"))

# ------------------------------------------ VS4 valores impossiveis no dominio
caso("vs4_01_massa_negativa", "PAN-C02", "VS4",
     receita('acucar = 200 g - 300 g;\npasso "x" por 5 min;'))
caso("vs4_02_quantidade_zero", "PAN-C02", "VS4",
     receita('acucar = 200 g - 200 g;\npasso "x" por 5 min;'))
caso("vs4_03_contagem_fracionaria", "PAN-C01", "VS4",
     receita('ovo = 2.5 un;\npasso "x" por 5 min;',
             ingredientes="ingrediente ovo : contagem;"))
caso("vs4_04_divisao_por_zero", "PAN-C03", "VS4",
     receita('acucar = 200 g / 0;\npasso "x" por 5 min;'))
caso("vs4_05_repetir_zero_vezes", "PAN-C04", "VS4",
     receita('acucar = 200 g;\npasso "x" por 5 min;',
             montagem="repetir 0 vezes em sequencia { executar p; }"))
caso("vs4_06_repetir_fracao", "PAN-C04", "VS4",
     receita('acucar = 200 g;\npasso "x" por 5 min;',
             montagem="repetir 2.5 vezes em sequencia { executar p; }"))

# ------------------------------- limites conhecidos (o checador ainda nao pega)
caso("lim_01_negativo_via_nome", "PAN-C02", "limite",
     receita('seja a = 300 g;\nacucar = 200 g - a;\npasso "x" por 5 min;'))
caso("lim_02_contagem_fracionaria_via_nome", "PAN-C01", "limite",
     receita('seja meio = 0.5;\novo = 5 un * meio;\npasso "x" por 5 min;',
             ingredientes="ingrediente ovo : contagem;"))
caso("lim_03_ingrediente_declarado_sem_uso", "PAN-E05", "limite",
     receita('acucar = 200 g;\npasso "x" por 5 min;',
             ingredientes="ingrediente acucar : massa;\n  ingrediente sal : massa;"))
caso("lim_04_tempo_escalado_pelo_autor", "PAN-O07", "limite",
     receita('acucar = 200 g;\npasso "x" por 40 min * 2;'))
caso("lim_05_passo_sem_tempo_no_total", "PAN-A01", "limite",
     receita('acucar = 200 g;\npasso "deixar descansar";'))
caso("lim_06_xicara_somada_com_grama", "PAN-F06", "limite",
     receita('acucar = 1 xic;\npasso "x" por 5 min;'))


def main():
    os.makedirs(DESTINO, exist_ok=True)
    for nome, esperado, categoria, fonte in CASOS:
        cabecalho = (f"// CATEGORIA: {categoria}\n"
                     f"// ESPERADO: {esperado or 'nenhum'}\n")
        caminho = os.path.join(DESTINO, f"{nome}.pan")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(cabecalho + fonte)
    print(f"{len(CASOS)} casos gravados em {DESTINO}")


if __name__ == "__main__":
    main()
