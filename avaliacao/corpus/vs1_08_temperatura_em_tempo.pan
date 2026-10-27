// CATEGORIA: VS1
// ESPERADO: PAN-F04
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 10 min a 30 min;
      }

      montagem {
        executar p;
      }
    }
