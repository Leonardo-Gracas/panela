// CATEGORIA: limite
// ESPERADO: PAN-C02
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        seja a = 300 g;
acucar = 200 g - a;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
