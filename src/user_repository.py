from src.db_connection import db_connection


class UserRepository:
    def create_user(self, user_id: int):
        return db_connection.execute_query(
            'INSERT INTO "users" (user_id, balance) VALUES (%s, %s) RETURNING *', [user_id, 1000])

    def find_user(self, user_id: int):
        return db_connection.execute_query(
            'SELECT * FROM "users" WHERE user_id = %s', [user_id])

    def send_money(self, sender_id: int, receiver_id: int, amount: int):
        with db_connection.get_connection().cursor() as cursor:
            cursor.execute(
                'UPDATE users SET balance = balance - %s WHERE id = %s', [amount, sender_id])
            cursor.execute(
                'UPDATE users SET balance = balance + %s WHERE id = %s', [amount, receiver_id])

            cursor.execute(
                'INSERT INTO transactions(sender_id, receiver_id, amount) VALUES(%s, %s, %s)',
                [sender_id, receiver_id, amount])

            db_connection.get_connection().commit()
