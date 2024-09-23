from abc import ABC, abstractmethod
from pymysql.connections import Connection

class IDatabaseConnection(ABC):
    @abstractmethod
    def get_connection(self) -> Connection:
        pass

    @abstractmethod
    def __enter__(self) -> Connection:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
