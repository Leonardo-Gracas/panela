// CATEGORIA: VS3
// ESPERADO: PAN-E06
    receita "Caso de teste" {
      rende 0 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
