// CATEGORIA: VS4
// ESPERADO: PAN-C04
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "x" por 5 min;
      }

      montagem {
        repetir 2.5 vezes em sequencia { executar p; }
      }
    }
