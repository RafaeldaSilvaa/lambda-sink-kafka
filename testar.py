import json

from src.features.lambda_sink.presentation.lambda_function import lambda_handler


def test_lambda_handler():
    # Simulando um evento de entrada
    event = [
   {
      "payload":{
         "topic":"test_topic",
         "partition":1,
         "offset":0,
         "key":"test_key",
         "value":{
            "data":{
                "id": 20,
               "field1":"value1",
               "field2":"value2",
               "field3":"value3",
               "status":True
            }
         },
         "headers":{

         },
         "timestamp":"2023-09-20T12:34:56Z"
      }
   }
]

    context = {}  # Você pode adicionar informações de contexto se necessário

    # Executando o handler
    response = lambda_handler(event, context)

    # Validando a resposta
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == "Processamento concluído com sucesso"


if __name__ == "__main__":
    test_lambda_handler()

    print("Teste executado com sucesso!")
