// CATEGORIA: VS3
// ESPERADO: PAN-E01
      receita "Caso de teste" {
        rende 4 porcoes;

        ingrediente acucar : massa;
ingrediente sal : massa;
        preparo q {
  seja base = 10 g;
  acucar = base;
}

        preparo p {
          sal = base;
  passo "x" por 5 min;
        }

        montagem {
          executar q;
  executar p;
        }
      }
