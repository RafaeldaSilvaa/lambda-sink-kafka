# src/cross_cutting/dependency_container.py
from dependency_injector import containers, providers
from src.features.lambda_sink.infrastructure.database.mysql_connection import MySQLConnection
#from src.features.lambda_sink.infrastructure.database.mysql_record_repository import MySQLRecordRepository
from src.features.lambda_sink.infrastructure.adapters.aws.secret_manager_adapter import SecretManagerAdapter
from src.features.lambda_sink.application.use_cases.process_records_use_case import ProcessRecordsUseCase
from src.cross_cutting.logging_antigo import TraceLogger
from src.features.lambda_sink.infrastructure.database.mysql_record_repository import MySQLRecordRepository
from src.features.lambda_sink.infrastructure.database.sql_query_builder import SimpleSQLQueryBuilder


class DependencyContainer(containers.DeclarativeContainer):
    """Container de Dependências para injeção de dependências."""

    # Fornecendo o logger
    logger = providers.Singleton(TraceLogger)

    # Fornecendo o SecretManager
    secret_manager = providers.Singleton(SecretManagerAdapter, secret_name="mysql_credential")

    # Fornecendo a conexão com o MySQL
    db_connection = providers.Singleton(
        MySQLConnection,
        secret_manager=secret_manager
    )

    sql_query_builder = providers.Singleton(
        SimpleSQLQueryBuilder
    )

    # Fornecendo o repositório
    record_repository = providers.Singleton(
        MySQLRecordRepository,
        db_connection=db_connection,
        query_builder = sql_query_builder
    )

    # Fornecendo o caso de uso
    process_records_use_case = providers.Singleton(
        ProcessRecordsUseCase,
        repository=record_repository,
    )