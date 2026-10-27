// CATEGORIA: VS3
// ESPERADO: PAN-E01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        seja dobro = acucar * 2;
acucar = 200 g;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
