// CATEGORIA: VS4
// ESPERADO: PAN-C03
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g / 0;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
