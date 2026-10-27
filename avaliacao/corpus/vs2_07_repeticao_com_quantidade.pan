// CATEGORIA: VS2
// ESPERADO: PAN-O05
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 5 min;
      }

      montagem {
        repetir 3 min vezes em sequencia { executar p; }
      }
    }
