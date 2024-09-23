import pymysql

# Conectar ao banco de dados MySQL
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='test_db'
)

try:
    with connection.cursor() as cursor:
        # Verificar se a tabela foi criada
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("Tabelas:", tables)

        # Verificar a estrutura da tabela "records"
        cursor.execute("DESCRIBE records;")
        table_structure = cursor.fetchall()
        print("Estrutura da tabela 'records':", table_structure)
finally:
    connection.close()
