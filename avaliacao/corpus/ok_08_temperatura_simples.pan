// CATEGORIA: controle
// ESPERADO: nenhum
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 40 min a 180 C;
      }

      montagem {
        executar p;
      }
    }
