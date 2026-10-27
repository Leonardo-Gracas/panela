// CATEGORIA: VS2
// ESPERADO: PAN-O03
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = (100 g + 100 g) * (2 g);
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
