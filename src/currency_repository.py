from src.db_connection import db_connection
from os import getenv
import requests


class CurrencyRepository:
    def get_currencies(self):
        return db_connection.execute_query('SELECT * FROM currencies')

    def get_currencies_for_user(self, userId: int):
        return db_connection.execute_query('SELECT * FROM users_currencies WHERE user_id = %s', [userId])

    def buy_currency_for_user(self, userId: int, crypto_name: str, amount: str):

        crypto = self.get_currencies_for_user(userId)

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
