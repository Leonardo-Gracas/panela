// CATEGORIA: VS2
// ESPERADO: PAN-O02
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 10 min a 180 C / 2;
      }

      montagem {
        executar p;
      }
    }
