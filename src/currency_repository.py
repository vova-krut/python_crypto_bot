from src.db_connection import db_connection


class CurrencyRepository:
    def get_currencies(self):
        result = db_connection.execute_query('SELECT * FROM currencies')

        return result
