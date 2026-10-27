// CATEGORIA: VS2
// ESPERADO: PAN-O01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 10 min a 180 C + 20 C;
      }

      montagem {
        executar p;
      }
    }
