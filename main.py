from src.database import connect_to_database
from src.create_tables import create_tables
from src.delete_tables import delete_tables
from src.etl import insert_data


if __name__ == "__main__":
    conn = connect_to_database()
    delete_tables(conn)
    create_tables(conn)
    insert_data(conn)