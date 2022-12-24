from src.sql_queries import insert_from_json
import os


def insert_data(conn) -> None:
    """
    #TODO write docs
    """
    cursor = conn.cursor()
    cursor.execute(insert_from_json.format(
        table_name="operations",
        file_name=os.path.join(os.getcwd(), "data/operations.json")
    ))

    cursor.execute(insert_from_json.format(
        table_name="currencies",
        file_name=os.path.join(os.getcwd(), "data/currencies.json")
    ))