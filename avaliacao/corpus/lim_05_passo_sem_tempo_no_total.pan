// CATEGORIA: limite
// ESPERADO: PAN-A01
    receita "Caso de teste" {
      rende 4 porcoes;

      ingrediente acucar : massa;

      preparo p {
        acucar = 200 g;
passo "deixar descansar";
      }

      montagem {
        executar p;
      }
    }
