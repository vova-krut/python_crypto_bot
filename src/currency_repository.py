from src.db_connection import db_connection
from os import getenv
import requests


class CurrencyRepository:
    def get_currencies(self):
        return db_connection.execute_query('SELECT * FROM currencies')

    def get_currencies_for_user(self, user_id: int):
        return db_connection.execute_query('SELECT currency_id, amount FROM users_currencies WHERE user_id = %s', [user_id])

    def send_crypto_to_user(self, sender_id: int, receiver_id: int, crypto_name: str, amount: str):
        crypto_id = db_connection.execute_query(
            'SELECT id from currencies WHERE currency_name = %s', [crypto_name])[0][0]
        crypto_amount = db_connection.execute_query(
            'SELECT amount FROM users_currencies WHERE user_id = %s AND currency_id = %s', [sender_id, crypto_id])

        if not crypto_amount:
            raise ValueError('User does not have this crypto')

        if crypto_amount[0][0] < float(amount):
            raise ValueError(
                'User does not have enough crypto to perform this operation')

        receiver_amount = db_connection.execute_query(
            'SELECT amount FROM users_currencies WHERE user_id = %s AND currency_id = %s', [receiver_id, crypto_id])

        if receiver_amount:
            self._add_crypto_to_user(sender_id, receiver_id, crypto_id, amount)

            return

        self._create_crypto_for_user(sender_id, receiver_id, crypto_id, amount)

    def _add_crypto_to_user(self, sender_id: int, receiver_id: int, crypto_id: int, amount: str):
        conn = db_connection.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE users_currencies SET amount = amount - %s WHERE user_id = %s AND currency_id = %s', [amount, sender_id, crypto_id])
            cursor.execute(
                'UPDATE users_currencies SET amount = amount + %s WHERE user_id = %s AND currency_id = %s', [amount, receiver_id, crypto_id])
            conn.commit()

    def _create_crypto_for_user(self, sender_id: int, receiver_id: int, crypto_id: int, amount: str):
        conn = db_connection.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE users_currencies SET amount = amount - %s WHERE user_id = %s AND currency_id = %s', [amount, sender_id, crypto_id])
            cursor.execute(
                'INSERT INTO users_currencies(user_id, currency_id, amount) VALUES(%s, %s, %s)', [receiver_id, crypto_id, amount])
            conn.commit()

    def buy_currency_for_user(self, user_id: int, crypto_name: str, amount: str):
        crypto_id = db_connection.execute_query(
            'SELECT id from currencies WHERE currency_name = %s', [crypto_name])[0][0]
        user_has_crypto = db_connection.execute_query(
            'SELECT amount FROM users_currencies WHERE user_id = %s AND currency_id = %s', [user_id, crypto_id])

        balance = db_connection.execute_query(
            'SELECT balance FROM users WHERE id = %s', [user_id])[0][0]

        price = self._get_price(crypto_name, amount)

        if (price > balance):
            raise ValueError("You don't have enough money to buy it")

        if user_has_crypto:
            self._update_user_crypto(user_id, crypto_id, amount, price)
            return

        self._add_user_crypto(user_id, crypto_id, amount, price)

    def _update_user_crypto(self, user_id: int, crypto_id: int, amount: str, price: float):
        conn = db_connection.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE users_currencies SET amount = amount + %s WHERE user_id = %s AND currency_id = %s', [amount, user_id, crypto_id])
            cursor.execute(
                'UPDATE users SET balance = balance - %s WHERE id = %s', [price, user_id])
            conn.commit()

    def _add_user_crypto(self, user_id: int, crypto_id: int, amount: str, price: float):
        conn = db_connection.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users_currencies(user_id, currency_id, amount) VALUES(%s, %s, %s)', [user_id, crypto_id, amount])
            cursor.execute(
                'UPDATE users SET balance = balance - %s WHERE id = %s', [price, user_id])
            conn.commit()

    def _get_price(self, crypto_name: str, amount: str):
        headers = {
            'X-CMC_PRO_API_KEY': getenv('API_TOKEN')
        }

        response = requests.get(
            f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={crypto_name}',
            headers=headers)

        coin_price = response.json(
        )['data'][crypto_name]['quote']['USD']['price']

        return coin_price * float(amount)
