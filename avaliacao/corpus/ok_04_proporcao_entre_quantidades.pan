// CATEGORIA: controle
// ESPERADO: nenhum
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        seja r = 400 g / 200 g;
acucar = 100 g * r;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
