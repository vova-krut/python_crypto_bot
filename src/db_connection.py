from psycopg2 import connect
from dotenv import load_dotenv
from os import getenv
from sys import exit
from src.sql_queries import delete_queries, create_queries, insert_currencies


class DbConnection:
    def __init__(self):
        load_dotenv()

        self._connection = self._initDbConnect()

        self._deleteTables()
        self._createTables()
        self._insertCurrencies()

    def _initDbConnect(self):
        return connect(dbname=getenv('PG_DBNAME'), user=getenv('PG_USER'),
                       password=getenv('PG_PASSWORD'), host=getenv('PG_HOST'))

    def _deleteTables(self):
        with self._connection.cursor() as cursor:
            try:
                for query in delete_queries:
                    cursor.execute(query)
            except Exception as e:
                print(f'Failed to execute a query: \n{query}.')
                print(e)
                exit(1)
            self._connection.commit()
            print(f'Successfully deleted tables.')

    def _createTables(self):
        with self._connection.cursor() as cursor:
            try:
                for query in create_queries:
                    cursor.execute(query)
            except Exception as e:
                print(f'Failed to execute a query: \n{query}.')
                print(e)
                exit(1)
            self._connection.commit()
            print(f'Successfully created tables.')

    def _insertCurrencies(self):
        with self._connection.cursor() as cursor:
            try:
                for query in insert_currencies:
                    cursor.execute(query)
            except Exception as e:
                print(f'Failed to execute a query: \n{insert_currencies}.')
                print(e)
                exit(1)
            self._connection.commit()
            print(f'Successfully inserted currencies.')

    def execute_query(self, query, vars=[]):
        with self._connection.cursor() as cursor:
            cursor.execute(query, vars)

            self._connection.commit()

            result = cursor.fetchall()
            return result

    def get_connection(self):
        return self._connection


db_connection = DbConnection()
