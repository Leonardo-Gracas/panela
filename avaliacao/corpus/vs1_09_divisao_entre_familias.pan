// CATEGORIA: VS1
// ESPERADO: PAN-F01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        seja r = 200 g / 10 min;
acucar = 100 g * r;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
