import json

create_transactions_table = '''
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users (id) NOT NULL,
        operation_id INT REFERENCES operations (id) NOT NULL,
        quantity NUMERIC NOT NULL,
        currency_id INT REFERENCES currencies (id) NOT NULL
    );
'''


create_operations_table = '''
    CREATE TABLE IF NOT EXISTS operations (
        id SERIAL PRIMARY KEY,
        operation TEXT NOT NULL,
        description TEXT NOT NULL
    );
'''


create_currencies_table = '''
    CREATE TABLE IF NOT EXISTS currencies (
        id SERIAL PRIMARY KEY,
        currency_name TEXT NOT NULL
    );
'''


create_users_table = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id INT
    );
'''

insert_currencies = []

with open('./src/data/currencies.json') as f:
    json_data = json.load(f)
    for payload in json_data:
        insert_currencies.append(
            f"INSERT INTO currencies(currency_name) Values ('{payload['currency_name']}');")

delete_transactions_table = 'DROP TABLE IF EXISTS transactions CASCADE;'
delete_operations_table = 'DROP TABLE IF EXISTS operations CASCADE;'
delete_currencies_table = 'DROP TABLE IF EXISTS currencies CASCADE;'
delete_users_table = 'DROP TABLE IF EXISTS users CASCADE;'


create_queries = [create_currencies_table, create_operations_table,
                  create_users_table, create_transactions_table]
delete_queries = [delete_users_table, delete_transactions_table,
                  delete_currencies_table, delete_operations_table]


insert_from_json = '''
    COPY {table_name}
    FROM "{file_name}"';
'''
