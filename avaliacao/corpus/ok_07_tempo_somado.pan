// CATEGORIA: controle
// ESPERADO: nenhum
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 30 min + 15 min;
      }

      montagem {
        executar p;
      }
    }
