from dataclasses import dataclass

from src.features.lambda_sink.domain.entities.record_value import RecordValue


@dataclass
class SinkRecord:
    topic: str
    partition: int
    offset: int
    key: str
    value: RecordValue
    headers: dict
    timestamp: str