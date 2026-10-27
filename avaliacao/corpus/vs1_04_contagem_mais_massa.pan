// CATEGORIA: VS1
// ESPERADO: PAN-F01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente ovo : contagem;

      preparo p {
        ovo = 2 un + 50 g;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
