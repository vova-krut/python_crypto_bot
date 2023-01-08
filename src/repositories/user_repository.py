from src.db_connection import db_connection
from src.repositories.currency_repository import CurrencyRepository


class UserRepository:
    def __init__(self) -> None:
        self._currency_repository = CurrencyRepository()

    def create_user(self, user_id: int):
        return db_connection.execute_query(
            'INSERT INTO users (id, balance) VALUES (%s, %s) RETURNING *', [user_id, 10000])

    def find_user(self, user_id: int):
        return db_connection.execute_query(
            'SELECT * FROM users WHERE id = %s', [user_id])

    def get_balance(self, user_id: int):
        currency_balance = self._currency_repository.get_currencies_for_user(
            user_id)
        usd_balance = db_connection.execute_query(
            'SELECT balance FROM users WHERE id = %s', [user_id])[0][0]

        return currency_balance, usd_balance
