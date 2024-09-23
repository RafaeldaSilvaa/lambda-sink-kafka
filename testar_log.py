import json
import logging
from typing import Any, List

from src.cross_cutting.logging import TraceLogger, MethodTraceContext

class MyService:
    """Classe de exemplo que contém métodos a serem rastreados."""
    def process_data(self, data: List[str]) -> str:
        return f"Processed {len(data)} items"

    def another_method(self, value: int) -> int:
        return value * 2

def lambda_handler(event: dict, context) -> dict:
    logger = TraceLogger()  # Cria uma instância do logger
    service = MyService()

    try:
        with MethodTraceContext(logger, service) as tracer:
            result = service.process_data(event.get("data", []))
            another_result = service.another_method(5)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "result": result,
                "another_result": another_result
            })
        }

    except Exception as e:
        logging.info(f"Erro no processamento: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps("Erro no processamento")
        }

# Teste
if __name__ == "__main__":
    test_event = {
        "data": ["item1", "item2", "item3"]
    }
    print(lambda_handler(test_event, None))
