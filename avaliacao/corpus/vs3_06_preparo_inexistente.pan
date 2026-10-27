// CATEGORIA: VS3
// ESPERADO: PAN-E03
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 5 min;
      }

      montagem {
        executar outro;
      }
    }
