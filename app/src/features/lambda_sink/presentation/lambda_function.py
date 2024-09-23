import json
import logging
from src.cross_cutting.container.dependency_container import DependencyContainer
from src.features.lambda_sink.domain.entities.sink_record import SinkRecord
from src.features.lambda_sink.domain.mappers.mappers import EventMapper
from typing import List

def lambda_handler(event: dict, context) -> dict:
    container = DependencyContainer()
    use_case = container.process_records_use_case()

    try:
        # Mapeamento de eventos para SinkRecord
        records: List[SinkRecord] = [
            EventMapper.map_event_to_sink_record(payload=e['payload']) for e in event
        ]

        # Execução do caso de uso
        use_case.execute(records=records)

        # Retorna sucesso
        return {
            "statusCode": 200,
            "body": json.dumps("Processamento concluído com sucesso")
        }

    except Exception as e:
        logging.info(f"Erro no processamento: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps("Erro no processamento")
        }
