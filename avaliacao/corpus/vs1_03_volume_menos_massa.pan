// CATEGORIA: VS1
// ESPERADO: PAN-F01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente agua : volume;

      preparo p {
        agua = 500 ml - 100 g;
passo "x" por 5 min;
      }

      montagem {
        executar p;
      }
    }
