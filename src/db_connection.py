from psycopg2 import connect
from os import getenv
from sys import exit
from src.sql_queries import delete_queries, create_queries, insert_currencies


class DbConnection:
    __instance = None

    @staticmethod
    def get_instance():
        if not DbConnection.__instance:
            DbConnection()

        return DbConnection.__instance

    def __init__(self):
        if not DbConnection.__instance:
            raise Exception(
                "DbConnection is a singleton class, use get_instance() instead")
        else:
            self._connection = self._initDbConnect()

            self._deleteTables()
            self._createTables()
            self._insertCurrencies()

            DbConnection.__instance = self

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

    @staticmethod
    def get_connection():
        return DbConnection._connection
