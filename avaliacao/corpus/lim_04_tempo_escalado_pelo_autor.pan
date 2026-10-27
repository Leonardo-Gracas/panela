// CATEGORIA: limite
// ESPERADO: PAN-O07
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 40 min * 2;
      }

      montagem {
        executar p;
      }
    }
