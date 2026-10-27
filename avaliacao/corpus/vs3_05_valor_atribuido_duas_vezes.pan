// CATEGORIA: VS3
// ESPERADO: PAN-E02
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
acucar = 50 g;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
