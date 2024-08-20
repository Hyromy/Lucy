import os
import shutil
import json
import mysql.connector.connection_cext
import mysql.connector.cursor_cext

class SQLHelper:
    def __init__(self) -> None:
        self.__conn: mysql.connector.connection_cext.CMySQLConnection
        self.connect()

    def connect(self) -> None:
        try:
            self.__conn = mysql.connector.connect(
                port = os.getenv("MYSQL_PORT"),
                host = os.getenv("MYSQL_HOST"),
                user = os.getenv("MYSQL_USER"),
                password = os.getenv("MYSQL_PASSWORD"),
                database = os.getenv("MYSQL_DATABASE"),
                charset = "utf8mb4",
                collation = "utf8mb4_unicode_ci",
                raise_on_warnings = True
            )

            self.__conn.autocommit = True

        except Exception as e:
            msg = "No se pudo conectar a la base de datos"
            print(f"\t(!!) {msg} -> {e.__cause__}")
    
    def close_conection(self) -> None:
        self.__conn.close()

    def import_db(self, input_file:str, cls_db = True, del_file = True) -> None:
        if not os.path.exists(input_file):
            msg = f"El archivo {input_file} no existe"
            raise FileNotFoundError(msg)
        
        elif not input_file.endswith(".sql"):
            msg = f"El archivo {input_file} no es un archivo sql"
            raise ValueError(msg)
        
        if cls_db:
            self.clear_db(clear = True)

        cursor = self.__conn.cursor()
        with open(input_file, 'r') as f:
            sql_commands = f.read().split(';')
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
        cursor.close()

        if del_file:
            os.remove(input_file)

    def export_db(self, out_file = "") -> None:
        cursor = self.__conn.cursor()
        tables = self.get_tables_name()
        with open(f"{out_file}.sql", "w") as f:
            for table in tables:
                cursor.execute(f"SHOW CREATE TABLE {table}")
                create_table = cursor.fetchone()[1]
                f.write(f"{create_table};\n\n")

                cursor.execute(f"SELECT * FROM {table}")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                for row in rows:
                    values = ', '.join([f"'{str(value)}'" if value is not None else 'NULL' for value in row])
                    insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({values});"
                    f.write(f"{insert_query}\n")
                f.write("\n")
        cursor.close()

    def get_tables_name(self) -> tuple[str]:
        cursor = self.__conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        tables = tuple([table[0] for table in tables])
        
        cursor.close()
        return tables

    def get_cols_name(self, table:str) -> tuple[str]:
        cursor = self.__conn.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = cursor.fetchall()
        columns = tuple([column[0] for column in columns])

        cursor.close()
        return columns

    def get_col_description(self, table:str) -> list[tuple[str]]:
        cursor = self.__conn.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        description = cursor.fetchall()

        cursor.close()
        return description

    def drop_table(self, table:str) -> None:
        cursor = self.__conn.cursor()
        cursor.execute(f"DROP TABLE {table}")
        cursor.close()

    def clear_table(self, table:str) -> None:
        cursor = self.__conn.cursor()
        cursor.execute(f"DELETE FROM {table}")
        cursor.close()

    def clear_db(self, *, clear = False) -> None:
        if not clear:
            return
        
        tables = list(self.get_tables_name())
        tries = len(tables)
        to_delete = []
        while tables and tries >= 0:
            for i in to_delete:
                tables.pop(i)
            to_delete.clear()

            for i, table in enumerate(tables):
                try:
                    self.drop_table(table)
                    to_delete.append(i)
                except:
                    tries -= 1
        
        if tries < 0:
            msg = "No se pudo limpiar la base de datos, Maximo de intentos alcanzado"
            raise Exception(msg)

    def cols_description_to_dict(self, desc:list[tuple[str]]) -> dict[str, str]:
        data = {}
        for col in desc:
            description = col[1].upper()
            if col[2] == "NO":
                description += " NOT NULL"

            if col[3] == "PRI":
                description += " PRIMARY KEY"
            elif col[3] == "MUL":
                description += " NOT NULL,"
                description += f" FOREIGN KEY ({col[0]})"
                description += f" REFERENCES {col[0][3:]}({col[0]})"
                description += " ON DELETE CASCADE ON UPDATE CASCADE"

            if col[4]:
                description += f" DEFAULT '{col[4]}'"

            if col[5] == "auto_increment":
                description += " AUTO_INCREMENT"

            data[col[0]] = description
        return data

    def get_logs_from_table(self, table:str) -> list[tuple]:
        cursor = self.__conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        logs = cursor.fetchall()

        cursor.close()
        return logs

    def load_cache(self, reload = False) -> None:
        if reload and os.path.exists("dbcache"):
            shutil.rmtree("dbcache")

        os.makedirs("dbcache", exist_ok = True)
        tables = self.get_tables_name()
        for table in tables:
            with open(f"dbcache/{table}.json", "w") as f:
                cache = {}
                data = self.cols_description_to_dict(
                    self.get_col_description(table)
                )
                cache["data"] = data
                cols_name = self.get_cols_name(table)
                for log in self.get_logs_from_table(table):
                    cache[log[0]] = {
                        cols_name[i]: log[i] for i in range(1, len(cols_name))
                    }
                json.dump(cache, f, indent = 4)

    def read_cache_files(self) -> tuple[str]:
        return tuple(os.listdir("dbcache"))

    def build_from_cache(self) -> None:
        if not os.path.exists("dbcache"):
            msg = "No hay archivos de cache para construir la base de datos"
            raise FileNotFoundError(msg)

        for cache_file_name in self.read_cache_files():
            with open(f"dbcache/{cache_file_name}", "r") as f:
                data = json.load(f)
                table_data = data.pop("data")
                cursor = self.__conn.cursor()

                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {cache_file_name[:-5]}")
                except:
                    pass

                create_table_sentence = f"CREATE TABLE {cache_file_name[:-5]} ("
                for key, value in table_data.items():
                    create_table_sentence += f"{key} {value}, "
                create_table_sentence = create_table_sentence[:-2] + ")"
                cursor.execute(create_table_sentence)

                for id_, dict_ in data.items():
                    insert_query = f"INSERT INTO {cache_file_name[:-5]} VALUES ({id_}, "
                    for _, value in dict_.items():
                        insert_query += f"'{value}', "
                    insert_query = insert_query[:-2] + ")"
                    cursor.execute(insert_query)
                cursor.close()