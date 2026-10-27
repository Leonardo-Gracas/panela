// CATEGORIA: controle
// ESPERADO: nenhum
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = (200 g + 50 g) * 3;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
