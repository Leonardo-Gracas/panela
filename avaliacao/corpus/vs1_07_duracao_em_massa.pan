// CATEGORIA: VS1
// ESPERADO: PAN-F03
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 200 g;
      }

      montagem {
        executar p;
      }
    }
