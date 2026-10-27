// CATEGORIA: VS3
// ESPERADO: PAN-E01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = base * 2;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
