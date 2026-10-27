// CATEGORIA: VS4
// ESPERADO: PAN-C02
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g - 300 g;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
