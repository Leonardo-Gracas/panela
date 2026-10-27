// CATEGORIA: limite
// ESPERADO: PAN-C01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente ovo : contagem;

      preparo p {
        seja meio = 0.5;
ovo = 5 un * meio;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
