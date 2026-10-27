// REJEITADO — VS2 (PAN-O02): temperatura nao escala.
receita "Erro de escala" {
  rende 4 porcoes;

  ingrediente farinha : massa;

  preparo base {
    farinha = 200 g;
    passo "Assar" por 30 min a 180 C * 2;
  }

  montagem {
    executar base;
  }
}
