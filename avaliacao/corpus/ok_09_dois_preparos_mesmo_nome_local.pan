// CATEGORIA: controle
// ESPERADO: nenhum
      receita "Caso de teste" {
        rende 4 porcoes;

        ingrediente acucar : massa;
ingrediente sal : massa;
        preparo q {
  acucar = 200 g;
  sal = 5 g;
}

        preparo p {
          acucar = 50 g;
  passo "x" por 5 min;
        }

        montagem {
          executar q;
  executar p;
        }
      }
