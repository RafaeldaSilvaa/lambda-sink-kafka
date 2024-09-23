from typing import Dict, Any, List

from src.features.lambda_sink.domain.interfaces.sql_query_builder import ISQLQueryBuilder

class SimpleSQLQueryBuilder(ISQLQueryBuilder):
    def build_insert_query(
        self,
        table_name: str,
        record: Dict[str, Any],
        primary_keys: List[str],
        metadata: List[Dict[str, Any]]
    ) -> str:
        """Gera a query de INSERT, excluindo chaves primárias e campos gerados automaticamente."""
        insert_fields: List[str] = []
        placeholders: List[str] = []

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

            # Apenas inclui o campo se ele está presente no record
            if field_name in record:
                insert_fields.append(field_name)
                placeholders.append('%s')

        # Monta os campos e placeholders para a query
        fields_str: str = ', '.join(insert_fields)
        placeholders_str: str = ', '.join(placeholders)

        # Retorna a query final de inserção
        return f"INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders_str})"

    def build_update_query(
        self,
        table_name: str,
        record: Dict[str, Any],
        primary_keys: List[str],
        metadata: List[Dict[str, Any]]
    ) -> str:
        """Gera a query de UPDATE, excluindo chaves primárias e campos gerados automaticamente."""
        update_fields: List[str] = []

        for field in metadata:
            field_name: str = field['name']

            extra_info: str = field.get('extra', '').lower()
            default_value: str = field.get('default', '').lower() if field.get('default') else ''

            # Ignora campos que são chaves primárias, auto_increment ou têm valores padrões automáticos (ex: CURRENT_TIMESTAMP)
            if any([
                field_name in primary_keys,
                'auto_increment' in extra_info,
                'current_timestamp' in default_value
            ]):
                continue

            if field_name in record:
                update_fields.append(f"{field_name} = %s")

        update_clause: str = ', '.join(update_fields)

        # Considerando que a chave primária seja passada para construir o WHERE
        where_clause: str = ' AND '.join([f"{pk} = %s" for pk in primary_keys])

        return f"UPDATE {table_name} SET {update_clause} WHERE {where_clause}"
