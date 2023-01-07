from src.db_connection import db_connection
from os import getenv
import requests


class CurrencyRepository:
    def get_currencies(self):
        return db_connection.execute_query('SELECT * FROM currencies')

    def get_currencies_for_user(self, user_id: int):
        return db_connection.execute_query('SELECT currency_id, amount FROM users_currencies WHERE user_id = %s', [user_id])

    def send_crypto_to_user(self, sender_id: int, receiver_id: int, crypto_name: str, amount: int):
        cryptos = self.get_currencies_for_user(sender_id)

    def buy_currency_for_user(self, user_id: int, crypto_name: str, amount: str):
        cryptos = self.get_currencies_for_user(user_id)
        crypto_id = db_connection.execute_query(
            'SELECT id from currencies WHERE currency_name = %s', [crypto_name])[0][0]

        balance = db_connection.execute_query(
            'SELECT balance FROM users WHERE id = %s', [user_id])[0][0]

        price = self._get_price(crypto_name, amount)

        if (price > balance):
            raise ValueError("You don't have enough money to buy it")

        user_owns_crypto = any([t[0] == crypto_id for t in cryptos])

        if user_owns_crypto:
            conn = db_connection.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE users_currencies SET amount = amount + %s WHERE user_id = %s AND currency_id = %s', [amount, user_id, crypto_id])
                cursor.execute(
                    'UPDATE users SET balance = balance - %s WHERE id = %s', [price, user_id])
                conn.commit()
            return
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
