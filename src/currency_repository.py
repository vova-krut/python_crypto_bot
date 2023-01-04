from src.db_connection import DbConnection


class CurrencyRepository:
    def __init__(self) -> None:
        self._conn = DbConnection.get_instance().get_connection()

    def get_currencies(self):
        with self._conn.cursor() as cursor:
            cursor.execute('SELECT * FROM currencies')
            self._conn.commit()

            result = cursor.fetchall()
            return result
