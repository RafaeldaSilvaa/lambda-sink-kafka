from src.features.lambda_sink.domain.entities.credentials_database import Credentials
from src.features.lambda_sink.domain.interfaces.database_connection_interface import IDatabaseConnection
from src.features.lambda_sink.domain.interfaces.secret_manager_interface import ISecretManager
from pymysql.connections import Connection
import pymysql
from typing import Optional, Any, Dict


class MySQLConnection(IDatabaseConnection):
    def __init__(self, secret_manager: ISecretManager) -> None:
        self.secret_manager: ISecretManager = secret_manager
        self._credentials: Optional[Credentials] = None

    def _get_credentials(self) -> Credentials:
        if self._credentials is None:
            creds_dict: Dict[str, Any] = self.secret_manager.get_secret()
            self._credentials = Credentials(**creds_dict)
        return self._credentials

    def get_connection(self) -> Connection:
        credentials = self._get_credentials()
        try:
            connection: Connection = pymysql.connect(
                host=credentials.host,
                user=credentials.username,
                password=credentials.password,
                database=credentials.database,
                port=credentials.port if credentials.port else 3306
            )
            return connection
        except pymysql.MySQLError as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def __enter__(self) -> Connection:
        self.connection: Connection = self.get_connection()
        return self.connection

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        if self.connection:
            self.connection.close()
