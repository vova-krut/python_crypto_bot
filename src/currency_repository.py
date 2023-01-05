from src.db_connection import db_connection
from os import getenv
import requests


class CurrencyRepository:
    def get_currencies(self):
        return db_connection.execute_query('SELECT * FROM currencies')

    def get_currencies_for_user(self, user_id: int):
        return db_connection.execute_query('SELECT * FROM users_currencies WHERE user_id = %s', [user_id])

    def send_crypto_to_user(self, sender_id: int, receiver_id: int, crypto_name: str, amount: int):
        cryptos = self.get_currencies_for_user(sender_id)

    def buy_currency_for_user(self, user_id: int, crypto_name: str, amount: str):
        cryptos = self.get_currencies_for_user(user_id)

        headers = {
            'X-CMC_PRO_API_KEY': getenv('API_TOKEN')
        }

        response = requests.get(
            f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={crypto_name}',
            headers=headers)

        coin_price = response.json(
        )['data'][crypto_name]['quote']['USD']['price']

        price = coin_price * float(amount)

        print(price)
