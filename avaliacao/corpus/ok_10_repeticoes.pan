// CATEGORIA: controle
// ESPERADO: nenhum
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 100 g;
passo "x" por 10 min;
      }

      montagem {
        repetir 2 vezes em sequencia { executar p; }
repetir 3 vezes em paralelo { executar p; }
      }
    }
