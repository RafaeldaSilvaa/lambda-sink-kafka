from src.features.lambda_sink.domain.entities.sink_record import SinkRecord
from src.features.lambda_sink.domain.interfaces.repository_interface import IRecordRepository


class ProcessRecordsUseCase:
    def __init__(self, repository: IRecordRepository):
        self.repository: IRecordRepository = repository

    def execute(self, records: SinkRecord):
        try:
            for record in records:
                if record.value.status:
                    self.repository.upsert(record=record.value.__dict__, table_name="records")

        except Exception as e:
            print(e)