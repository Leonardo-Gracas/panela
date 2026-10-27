// CATEGORIA: VS4
// ESPERADO: PAN-C01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente ovo : contagem;

      preparo p {
        ovo = 2.5 un;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
