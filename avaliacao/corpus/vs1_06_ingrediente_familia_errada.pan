// CATEGORIA: VS1
// ESPERADO: PAN-F05
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 250 ml;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
