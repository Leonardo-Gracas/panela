// CATEGORIA: limite
// ESPERADO: PAN-E05
      receita "Caso de teste" {
        rende 4 porcoes;

        ingrediente acucar : massa;
ingrediente sal : massa;

        preparo p {
          acucar = 200 g;
  passo "x" por 5 min;
        }

        montagem {
          executar p;
        }
      }
