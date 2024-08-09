from dotenv import load_dotenv
load_dotenv("config.env")

import os
import shutil
import mysql
import mysql.connector
import mysql.connector.cursor
import json

class MySQLHelper:
    def __init__(self) -> None:
        self.conn:mysql.connector.MySQLConnection
        self.connect()

    def connect(self) -> None:
        self.conn = mysql.connector.connect(
            port = os.getenv("MYSQL_PORT"),
            host = os.getenv("MYSQL_HOST"),
            user = os.getenv("MYSQL_USER"),
            password = os.getenv("MYSQL_PASSWORD"),
            database = os.getenv("MYSQL_DATABASE"),
            charset = "utf8mb4",
            collation = "utf8mb4_unicode_ci",
            raise_on_warnings = True
        )

        self.conn.autocommit = True

    def close(self) -> None:
        self.conn.close()

    def get_cursor(self) -> mysql.connector.cursor.MySQLCursor:
        return self.conn.cursor()
    
    def export_db(self, output_file:str = "") -> None:
        output_file += ".sql"

        cursor = self.get_cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        with open(output_file, 'w') as f:
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SHOW CREATE TABLE {table_name}")
                create_table_query = cursor.fetchone()[1]
                f.write(f"{create_table_query};\n\n")

                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                for row in rows:
                    values = ', '.join([f"'{str(value)}'" if value is not None else 'NULL' for value in row])
                    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({values});"
                    f.write(f"{insert_query}\n")
                f.write("\n")

        cursor.close()
        print(f"Base de datos exportada a {output_file}")

    def import_db(self, input_file:str, drop_tables:bool = True) -> None:
        if not os.path.exists(input_file):
            print("El archivo no existe")
            return
        
        elif not input_file.endswith(".sql"):
            print("El archivo debe ser un archivo SQL")
            return
        
        if drop_tables:
            self.drop_tables()
            print("Tablas previas eliminadas")

        cursor = self.get_cursor()
        with open(input_file, 'r') as f:
            sql_commands = f.read().split(';')
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)

        cursor.close()
        print(f"Base de datos importada desde {input_file}")

    def drop_tables(self) -> None:
        cursor = self.get_cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE {table_name}")

        cursor.close()

    def get_tables_name(self) -> tuple[str]:
        cursor = self.get_cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()

        tb = []
        for table in tables:
            tb.append(table[0])

        return tuple(tb)

    def get_atributes(self,table:str) -> tuple[str]:
        cursor = self.get_cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = cursor.fetchall()
        cursor.close()

        cols = []
        for column in columns:
            cols.append(column[0])

        return tuple(cols)

    def read_all_logs(self) -> dict:
        cursor = self.get_cursor()
        result = {}
        for table in self.get_tables_name():
            cursor.execute(f"SELECT * FROM {table}")
            logs = cursor.fetchall()

            result[table] = logs

        return result
    
    def db_to_cache(self) -> None:
        os.makedirs("dbcache", exist_ok = True)
        tb_names = self.get_tables_name()

        for tb_name in tb_names:
            with open(f"dbcache/{tb_name}.json", "w") as f:
                cursor = self.get_cursor()
                cursor.execute(f"SELECT * FROM {tb_name}")
                logs = cursor.fetchall()

                data = {}
                atributes = self.get_atributes(tb_name)
                for log in logs:
                    atribute = {}
                    for atr in atributes:
                        if atr == "id":
                            continue
                        atribute[atr] = log[atributes.index(atr)]
                    data[log[0]] = atribute

                json.dump(data, f, indent = 4)
                cursor.close()

    def reload_db_cache(self) -> None:
        if os.path.exists("dbcache"):
            shutil.rmtree("dbcache")

        self.db_to_cache()