// CATEGORIA: VS1
// ESPERADO: PAN-F02
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g + 5;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
