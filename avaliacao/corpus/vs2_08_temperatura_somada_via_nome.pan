// CATEGORIA: VS2
// ESPERADO: PAN-O01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        seja forno = 180 C;
acucar = 200 g;
passo "x" por 10 min a forno + 10 C;
      }

      montagem {
        executar p;
      }
    }
