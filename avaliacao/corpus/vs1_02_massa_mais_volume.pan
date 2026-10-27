// CATEGORIA: VS1
// ESPERADO: PAN-F01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g + 100 ml;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
