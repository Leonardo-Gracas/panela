// CATEGORIA: VS3
// ESPERADO: PAN-E04
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        sal = 5 g;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
