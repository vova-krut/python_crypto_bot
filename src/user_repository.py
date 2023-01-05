from src.db_connection import db_connection


class UserRepository:
    def create_user(self, user_id: int):
        result = db_connection.execute_query(
            'INSERT INTO "users" (user_id) VALUES (%s) RETURNING *', [user_id])

        return result

    def find_user(self, user_id: int):
        result = db_connection.execute_query(
            'SELECT * FROM "users" WHERE user_id = %s', [user_id])

        return result
