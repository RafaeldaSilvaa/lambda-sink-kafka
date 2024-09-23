import pymysql
import logging
from typing import Dict, Any, List, Tuple

from src.features.lambda_sink.domain.interfaces.database_connection_interface import IDatabaseConnection
from src.features.lambda_sink.domain.interfaces.sql_query_builder import ISQLQueryBuilder
from pymysql.connections import Connection

class MySQLRecordRepository:
    def __init__(self, db_connection: IDatabaseConnection, query_builder: ISQLQueryBuilder) -> None:
        self.db_connection: IDatabaseConnection = db_connection
        self.query_builder: ISQLQueryBuilder = query_builder

    def _validate_fields(self, record: Dict[str, Any], metadata: List[Dict[str, Any]]) -> None:
        """Valida os campos obrigatórios no record, exceto aqueles com valores gerados automaticamente."""
        for field in metadata:
            field_name: str = field['name']

            extra_info: str = field.get('extra', '').lower()
            default_value: str = field.get('default', '').lower() if field.get('default') else ''

            # Ignora campos que são chaves primárias, auto_increment ou têm valores padrões automáticos (ex: CURRENT_TIMESTAMP)
            if any([
                'auto_increment' in extra_info,
                'current_timestamp' in default_value
            ]):
                continue

            # Valida se campos NOT NULL estão presentes no record
            if not field['null'] and field_name not in record:
                raise ValueError(f"Field '{field_name}' is required and cannot be null.")

    def get_table_metadata(self, table_name: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Obtém metadados da tabela e retorna as colunas e as chaves primárias (suportando chaves compostas)."""
        connection: Connection = self.db_connection.get_connection()
        try:
            with connection.cursor() as cursor:
                # Pegar metadados da tabela (nome dos campos e tipos)
                cursor.execute(f"DESCRIBE {table_name}")
                metadata: List[Dict[str, Any]] = []
                for column in cursor.fetchall():
                    metadata.append({
                        'name': column[0],
                        'null': column[2] == 'YES',
                        'default': column[4],  # Captura o valor padrão
                        'extra': column[5]  # Captura 'auto_increment' ou 'on update CURRENT_TIMESTAMP'
                    })

                # Pegar todas as colunas que são chave primária (caso haja mais de uma)
                cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
                primary_keys: List[str] = [row[4] for row in cursor.fetchall()]  # Nome das colunas que compõem a chave primária

                return metadata, primary_keys
        finally:
            connection.close()

    def record_exists(self, table_name: str, primary_keys: List[str], record: Dict[str, Any]) -> bool:
        """Verifica se um registro existe baseado nas colunas de chave primária."""
        connection: Connection = self.db_connection.get_connection()
        try:
            # Construção da cláusula WHERE para múltiplas chaves primárias
            where_clause: str = ' AND '.join([f"{key} = %s" for key in primary_keys])
            exists_query: str = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"

            # Captura os valores das chaves primárias no record
            key_values: Tuple[Any, ...] = tuple(record[key] for key in primary_keys)

            with connection.cursor() as cursor:
                cursor.execute(exists_query, key_values)
                return cursor.fetchone()[0] > 0
        finally:
            connection.close()

    def upsert(self, record: Dict[str, Any], table_name: str) -> None:
        connection: Connection = self.db_connection.get_connection()
        try:
            metadata, primary_keys = self.get_table_metadata(table_name)

            # Monta os valores (exclui as chaves primárias no caso do UPDATE)
            values: Tuple[Any, ...] = tuple(record[field['name']] for field in metadata if
                           field['name'] in record and field['name'] not in primary_keys)

            # Verifica se o registro existe
            if self.record_exists(table_name, primary_keys, record):
                # Validação para UPDATE: deve garantir que todas as chaves primárias estão no record
                for key in primary_keys:
                    if key not in record:
                        raise ValueError(f"O campo {key} é obrigatório para atualização.")
                sql: str = self.query_builder.build_update_query(table_name, record, primary_keys, metadata)
                values += tuple(record[key] for key in primary_keys)
            else:
                # Validação para INSERT
                self._validate_fields(record, metadata)
                sql: str = self.query_builder.build_insert_query(table_name, record, primary_keys, metadata)

            with connection.cursor() as cursor:
                cursor.execute(sql, values)
            connection.commit()
        except pymysql.MySQLError as e:
            logging.error(f"Erro ao salvar o registro: {e}")
            connection.rollback()
        except ValueError as ve:
            logging.error(f"Validação falhou: {ve}")
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()
