from psycopg2 import connect
from os import getenv
from sys import exit
from src.sql_queries import delete_queries, create_queries


class DbConnection:
    def __init__(self) -> None:
        self._connection = self._initDbConnect()
        self._deleteTables()
        self._createTables()

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
            finally:
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
            finally:
                self._connection.commit()
                print(f'Successfully created tables.')

    def get_connection(self):
        return self._connection
