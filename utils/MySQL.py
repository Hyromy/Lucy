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
    
    def export_db(self, output_file = "") -> None:
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

    def import_db(self, input_file:str, drop_tables = True, delete_file = True) -> None:
        if not os.path.exists(input_file):
            return
        
        elif not input_file.endswith(".sql"):
            return
        
        if drop_tables:
            self.drop_tables()

        cursor = self.get_cursor()
        with open(input_file, 'r') as f:
            sql_commands = f.read().split(';')
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)

        cursor.close()

        if delete_file:
            os.remove(input_file)

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

                data = {
                    "data": self.table_sql_to_json_data(tb_name)
                }

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

    def table_sql_to_json_data(self, table_name:str) -> dict:
        cursor = self.get_cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()

        data = {}
        for column in columns:
            sentencce = column[1].upper()
            if column[2] == "NO":
                sentencce += " NOT NULL"
            if column[3] == "PRI":
                sentencce += " PRIMARY KEY"
            if column[4] != None:
                sentencce += f" DEFAULT '{column[4]}'"
            if column[5] == "auto_increment":
                sentencce += " AUTO_INCREMENT"

            data[column[0]] = sentencce
        return data

    def reload_db_cache(self) -> None:
        if os.path.exists("dbcache"):
            shutil.rmtree("dbcache")

        self.db_to_cache()

    def create_table(self, table_name:str, columns:tuple[str]) -> None:
        if table_name in self.get_tables_name():
            return
        
        cursor = self.get_cursor()
        query = f"CREATE TABLE {table_name} ("
        for column in columns:
            query += f"{column}, "
        query = query[:-2] + ")"

        cursor.execute(query)
        cursor.close()

    def insert(self, table_name:str, atr:tuple[str], values:tuple) -> None:
        atr = str(atr).replace("'", "")
        
        cursor = self.get_cursor()
        query = f"INSERT INTO {table_name} {atr} VALUES {values}"

        cursor.execute(query)
        cursor.close()

    def build_from_cache(self, table_name:str) -> None:
        if not os.path.exists(f"dbcache/{table_name}.json"):
            return

        with open(f"dbcache/{table_name}.json", "r") as f:
            data = json.load(f)

        for key, value in data.items():
            if (key == "data"):
                colums = list(value)
                for i, atr in enumerate(colums):
                    colums[i] = f"{atr} {value[atr]}"
                self.create_table(table_name, tuple(colums))                

            else:
                atr = list(value)
                atr.insert(0, "id")

                values = list(value.values())
                values.insert(0, key)
                
                self.insert(table_name, tuple(atr), tuple(values))