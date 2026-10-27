// REJEITADO — VS1 (PAN-F01): soma de familias diferentes.
receita "Erro de familia" {
  rende 4 porcoes;

  ingrediente farinha : massa;

  preparo base {
    farinha = 200 g + 30 min;
    passo "Misturar" por 5 min;
  }

  montagem {
    executar base;
  }
}
