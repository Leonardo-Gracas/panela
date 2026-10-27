// REJEITADO — VS3 (PAN-E01): nome local de um preparo usado em outro.
receita "Erro de escopo" {
  rende 4 porcoes;

  ingrediente acucar  : massa;
  ingrediente farinha : massa;

  preparo massa {
    seja base = 200 g;
    acucar = base;
    passo "Misturar" por 5 min;
  }

  preparo cobertura {
    farinha = base * 2;
    passo "Bater" por 3 min;
  }

  montagem {
    executar massa;
    executar cobertura;
  }
}
