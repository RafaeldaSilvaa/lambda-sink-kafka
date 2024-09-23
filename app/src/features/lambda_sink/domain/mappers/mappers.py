from src.features.lambda_sink.domain.entities.record_value import RecordValue
from src.features.lambda_sink.domain.entities.sink_record import SinkRecord


class EventMapper:
    @staticmethod
    def map_event_to_sink_record(payload: dict) -> SinkRecord:
        value = RecordValue(**payload['value']["data"])
        return SinkRecord(
            topic=payload['topic'],
            partition=payload['partition'],
            offset=payload['offset'],
            key=payload['key'],
            value=value,
            headers=payload['headers'],
            timestamp=payload['timestamp']
        )