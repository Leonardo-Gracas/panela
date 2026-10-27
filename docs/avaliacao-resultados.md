# Avaliacao da verificacao semantica

Corpus: 52 programas (42 com erro proposital, 10 corretos).

| Categoria | Casos | Detectados | Escaparam | Falsos positivos | Taxa |
|---|---|---|---|---|---|
| Coerencia de familia | 10 | 10 | 0 | 0 | 100% |
| Operacao propria da familia | 10 | 10 | 0 | 0 | 100% |
| Nomes e identidade | 10 | 10 | 0 | 0 | 100% |
| Valores impossiveis no dominio | 6 | 6 | 0 | 0 | 100% |
| Limites conhecidos (fora do alcance atual) | 6 | 1 | 5 | 0 | 17% |
| Programas corretos (controle) | 10 | 0 | 0 | 0 | 100% sem alarme falso |
| **Total** | **52** | **37** | **5** | **0** | — |

## Detectados com codigo diferente do previsto

- `lim_06_xicara_somada_com_grama.pan`: previsto PAN-F06, obtido PAN-F05

## Casos problematicos

- `lim_01_negativo_via_nome.pan`: escapou (previsto PAN-C02, obtido None)
- `lim_02_contagem_fracionaria_via_nome.pan`: escapou (previsto PAN-C01, obtido None)
- `lim_03_ingrediente_declarado_sem_uso.pan`: escapou (previsto PAN-E05, obtido None)
- `lim_04_tempo_escalado_pelo_autor.pan`: escapou (previsto PAN-O07, obtido None)
- `lim_05_passo_sem_tempo_no_total.pan`: escapou (previsto PAN-A01, obtido None)

## Caso a caso

| Arquivo | Categoria | Previsto | Obtido | Resultado |
|---|---|---|---|---|
| `lim_01_negativo_via_nome.pan` | limite | PAN-C02 | — | escapou |
| `lim_02_contagem_fracionaria_via_nome.pan` | limite | PAN-C01 | — | escapou |
| `lim_03_ingrediente_declarado_sem_uso.pan` | limite | PAN-E05 | — | escapou |
| `lim_04_tempo_escalado_pelo_autor.pan` | limite | PAN-O07 | — | escapou |
| `lim_05_passo_sem_tempo_no_total.pan` | limite | PAN-A01 | — | escapou |
| `lim_06_xicara_somada_com_grama.pan` | limite | PAN-F06 | PAN-F05 | detectado (codigo diferente) |
| `ok_01_basico.pan` | controle | — | — | ok |
| `ok_02_soma_mesma_familia.pan` | controle | — | — | ok |
| `ok_03_escala_por_numero.pan` | controle | — | — | ok |
| `ok_04_proporcao_entre_quantidades.pan` | controle | — | — | ok |
| `ok_05_precedencia.pan` | controle | — | — | ok |
| `ok_06_parenteses.pan` | controle | — | — | ok |
| `ok_07_tempo_somado.pan` | controle | — | — | ok |
| `ok_08_temperatura_simples.pan` | controle | — | — | ok |
| `ok_09_dois_preparos_mesmo_nome_local.pan` | controle | — | — | ok |
| `ok_10_repeticoes.pan` | controle | — | — | ok |
| `vs1_01_massa_mais_tempo.pan` | VS1 | PAN-F01 | PAN-F01 | detectado |
| `vs1_02_massa_mais_volume.pan` | VS1 | PAN-F01 | PAN-F01 | detectado |
| `vs1_03_volume_menos_massa.pan` | VS1 | PAN-F01 | PAN-F01 | detectado |
| `vs1_04_contagem_mais_massa.pan` | VS1 | PAN-F01 | PAN-F01 | detectado |
| `vs1_05_quantidade_mais_numero.pan` | VS1 | PAN-F02 | PAN-F02 | detectado |
| `vs1_06_ingrediente_familia_errada.pan` | VS1 | PAN-F05 | PAN-F05 | detectado |
| `vs1_07_duracao_em_massa.pan` | VS1 | PAN-F03 | PAN-F03 | detectado |
| `vs1_08_temperatura_em_tempo.pan` | VS1 | PAN-F04 | PAN-F04 | detectado |
| `vs1_09_divisao_entre_familias.pan` | VS1 | PAN-F01 | PAN-F01 | detectado |
| `vs1_10_soma_via_nome_local.pan` | VS1 | PAN-F01 | PAN-F01 | detectado |
| `vs2_01_temperatura_somada.pan` | VS2 | PAN-O01 | PAN-O01 | detectado |
| `vs2_02_temperatura_escalada.pan` | VS2 | PAN-O02 | PAN-O02 | detectado |
| `vs2_03_temperatura_dividida.pan` | VS2 | PAN-O02 | PAN-O02 | detectado |
| `vs2_04_massa_vezes_massa.pan` | VS2 | PAN-O03 | PAN-O03 | detectado |
| `vs2_05_volume_vezes_tempo.pan` | VS2 | PAN-O03 | PAN-O03 | detectado |
| `vs2_06_numero_dividido_por_quantidade.pan` | VS2 | PAN-O04 | PAN-O04 | detectado |
| `vs2_07_repeticao_com_quantidade.pan` | VS2 | PAN-O05 | PAN-O05 | detectado |
| `vs2_08_temperatura_somada_via_nome.pan` | VS2 | PAN-O01 | PAN-O01 | detectado |
| `vs2_09_temperatura_escalada_via_nome.pan` | VS2 | PAN-O02 | PAN-O02 | detectado |
| `vs2_10_quantidade_vezes_quantidade_em_parenteses.pan` | VS2 | PAN-O03 | PAN-O03 | detectado |
| `vs3_01_nome_inexistente.pan` | VS3 | PAN-E01 | PAN-E01 | detectado |
| `vs3_02_local_de_outro_preparo.pan` | VS3 | PAN-E01 | PAN-E01 | detectado |
| `vs3_03_ingrediente_nao_declarado.pan` | VS3 | PAN-E04 | PAN-E04 | detectado |
| `vs3_04_ingrediente_duplicado.pan` | VS3 | PAN-E02 | PAN-E02 | detectado |
| `vs3_05_valor_atribuido_duas_vezes.pan` | VS3 | PAN-E02 | PAN-E02 | detectado |
| `vs3_06_preparo_inexistente.pan` | VS3 | PAN-E03 | PAN-E03 | detectado |
| `vs3_07_preparo_duplicado.pan` | VS3 | PAN-E02 | PAN-E02 | detectado |
| `vs3_08_ingrediente_usado_antes_do_valor.pan` | VS3 | PAN-E01 | PAN-E01 | detectado |
| `vs3_09_nome_local_dentro_de_repeticao.pan` | VS3 | PAN-E03 | PAN-E03 | detectado |
| `vs3_10_rende_zero.pan` | VS3 | PAN-E06 | PAN-E06 | detectado |
| `vs4_01_massa_negativa.pan` | VS4 | PAN-C02 | PAN-C02 | detectado |
| `vs4_02_quantidade_zero.pan` | VS4 | PAN-C02 | PAN-C02 | detectado |
| `vs4_03_contagem_fracionaria.pan` | VS4 | PAN-C01 | PAN-C01 | detectado |
| `vs4_04_divisao_por_zero.pan` | VS4 | PAN-C03 | PAN-C03 | detectado |
| `vs4_05_repetir_zero_vezes.pan` | VS4 | PAN-C04 | PAN-C04 | detectado |
| `vs4_06_repetir_fracao.pan` | VS4 | PAN-C04 | PAN-C04 | detectado |
