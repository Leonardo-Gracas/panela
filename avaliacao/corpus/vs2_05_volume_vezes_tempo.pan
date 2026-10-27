// CATEGORIA: VS2
// ESPERADO: PAN-O03
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente agua : volume;

      preparo p {
        agua = 100 ml * 2 min;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
