create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT NOT NULL,
        user_id INT REFERENCES users (user_id) NOT NULL,
        operation_id INT REFERENCES operations (operation_id) NOT NULL,
        quantity NUMERIC NOT NULL,
        currency_id INT REFERENCES currencies (currency_id) NOT NULL,
        PRIMARY KEY (transaction_id)
    );
"""


create_operations_table = """
    CREATE TABLE IF NOT EXISTS operations (
        operation_id SERIAL,
        operation TEXT NOT NULL,
        description TEXT NOT NULL,
        PRIMARY KEY (operation_id)
    );
"""


create_currencies_table = """
    CREATE TABLE IF NOT EXISTS currencies (
        currency_id SERIAL,
        currency_name TEXT NOT NULL,
        PRIMARY KEY (currency_id)
    );
"""


create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL,
        user_name TEXT,
        PRIMARY KEY (user_id)
    );
"""

delete_transactions_table = "DROP TABLE IF EXISTS transactions;"
delete_operations_table = "DROP TABLE IF EXISTS operations;"
delete_currencies_table = "DROP TABLE IF EXISTS currencies;"
delete_users_table = "DROP TABLE IF EXISTS users;"


create_queries = [create_currencies_table, create_operations_table, create_users_table, create_transactions_table]
delete_queries = [delete_currencies_table, delete_operations_table, delete_users_table, delete_transactions_table]


insert_from_json = """
    COPY {table_name}
    FROM '{file_name}';
"""