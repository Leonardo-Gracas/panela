// CATEGORIA: VS1
// ESPERADO: PAN-F01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        seja t = 30 min;
acucar = 200 g + t;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
