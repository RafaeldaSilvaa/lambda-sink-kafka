from dataclasses import dataclass


@dataclass
class RecordValue:
    id: int
    field1: str
    field2: str
    field3: str
    status: bool = False