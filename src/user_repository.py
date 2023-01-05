from src.db_connection import db_connection
from src.currency_repository import CurrencyRepository


class UserRepository:
    def __init__(self) -> None:
        self._curr_repository = CurrencyRepository()

    def create_user(self, user_id: int):
        return db_connection.execute_query(
            'INSERT INTO users (user_id, balance) VALUES (%s, %s) RETURNING *', [user_id, 1000])

    def find_user(self, user_id: int):
        return db_connection.execute_query(
            'SELECT * FROM users WHERE user_id = %s', [user_id])

    def get_balance(self, user_id: int):
        curr_balance = self._curr_repository.get_currencies_for_user(user_id)
        usd_balance = db_connection.execute_query(
            'SELECT balance FROM users WHERE user_id = %s', [user_id])

        return [*curr_balance, *usd_balance]
