// Exemplo 2 — repeticao em sequencia.
// Cada fornada ocupa a frigideira sozinha, entao o tempo soma.

receita "Panqueca simples" {
  rende 4 porcoes;

  ingrediente farinha : massa;
  ingrediente leite   : volume;
  ingrediente ovo     : contagem;
  ingrediente manteiga: massa;

  preparo lote {
    farinha  = 125 g;
    leite    = 250 ml;
    ovo      = 2 un;
    manteiga = 15 g;

    passo "Bater tudo ate ficar liso" por 3 min;
    passo "Fritar dos dois lados" por 6 min;
  }

  montagem {
    repetir 3 vezes em sequencia {
      executar lote;
    }
  }
}
