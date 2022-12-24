import os
import psycopg2


class DbConnection:
    def __init__(self) -> None:
        self.__connection = self.__initDbConnect()
        self.__createTables()

    def __initDbConnect(self):
        return psycopg2.connect(dbname=os.getenv('PG_DBNAME'), user=os.getenv('PG_USER'),
                                password=os.getenv('PG_PASSWORD'), host=os.getenv('PG_HOST'))

    def __createTables(self):
        with self.__connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                                id SERIAL PRIMARY KEY,
                                email VARCHAR(255) NOT NULL UNIQUE,
                                password VARCHAR(255) NOT NULL,
                                name VARCHAR(255) NOT NULL)''')
            self.__connection.commit()

    def get_connection(self):
        return self.__connection
