// CATEGORIA: VS2
// ESPERADO: PAN-O04
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 2 / 200 g;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
