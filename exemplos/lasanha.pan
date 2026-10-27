// Exemplo 3 — repeticao em paralelo, nome local com 'seja' e proporcao.
// As tres camadas vao ao forno juntas: os ingredientes somam, o tempo nao.

receita "Lasanha de tres camadas" {
  rende 6 porcoes;

  ingrediente massa_pronta : massa;
  ingrediente molho        : volume;
  ingrediente queijo       : massa;
  ingrediente presunto     : massa;

  preparo camada {
    seja recheio = 240 g;          // nome auxiliar: nao vai para as compras

    massa_pronta = 150 g;
    molho        = 200 ml;
    queijo       = recheio / 2;    // metade do recheio
    presunto     = recheio / 2;

    passo "Montar a camada" por 4 min;
  }

  preparo forno {
    passo "Assar a lasanha montada" por 35 min a 200 C;
  }

  montagem {
    repetir 3 vezes em paralelo {
      executar camada;
    }
    executar forno;
  }
}
