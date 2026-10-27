// CATEGORIA: limite
// ESPERADO: PAN-F06
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 1 xic;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
