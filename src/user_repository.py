from src.db_connection import DbConnection


class UserRepository:
    def __init__(self) -> None:
        self._conn = DbConnection().get_connection()

    def create_user(self, user_id: int):
        with self._conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "users" (user_id) VALUES (%s) RETURNING *', [user_id])
            self._conn.commit()

            result = cursor.fetchall()
            return result

    def find_user(self, user_id: int):
        with self._conn.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM "users" WHERE user_id = %s', [user_id])
            self._conn.commit()

            result = cursor.fetchone()
            return result
