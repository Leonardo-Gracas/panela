// Exemplo 1 — bolo de cenoura com cobertura.
// Mostra escopo (dois acucares), escala por porcoes e tempo total.

receita "Bolo de cenoura" {
  rende 12 porcoes;

  ingrediente acucar   : massa;
  ingrediente farinha  : massa;
  ingrediente cenoura  : massa;
  ingrediente ovo      : contagem;
  ingrediente oleo     : volume;
  ingrediente chocolate: massa;
  ingrediente leite    : volume;

  preparo massa {
    acucar  = 200 g;
    farinha = acucar * 1.5;      // proporcao, nao numero magico
    cenoura = 300 g;
    ovo     = 3 un;
    oleo    = 150 ml;

    passo "Bater cenoura, ovo e oleo no liquidificador" por 5 min;
    passo "Misturar farinha e acucar" por 4 min;
    passo "Assar" por 40 min a 180 C;
  }

  preparo cobertura {
    acucar    = 50 g;            // mesmo nome, outro escopo
    chocolate = 100 g;
    leite     = 100 ml;

    passo "Derreter o chocolate com o leite" por 8 min;
    passo "Juntar o acucar e mexer" por 2 min;
  }

  montagem {
    executar massa;
    executar cobertura;
  }
}
