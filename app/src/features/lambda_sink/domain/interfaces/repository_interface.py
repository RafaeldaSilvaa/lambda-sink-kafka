from abc import ABC, abstractmethod

from src.features.lambda_sink.domain.entities.record_value import RecordValue


class IRecordRepository(ABC):
    @abstractmethod
    def upsert(self, record: RecordValue, table_name: str) -> None:
        pass
