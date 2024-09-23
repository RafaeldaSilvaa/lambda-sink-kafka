from abc import ABC, abstractmethod
from typing import Dict, Any, List


class ISQLQueryBuilder(ABC):
    @abstractmethod
    def build_insert_query(self, table_name: str, record: Dict[str, Any], primary_keys: List[str], metadata: List[Dict[str, Any]]) -> str:
        pass

    @abstractmethod
    def build_update_query(self, table_name: str, record: Dict[str, Any], primary_keys: List[str], metadata: List[Dict[str, Any]]) -> str:

        pass