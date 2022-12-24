from src.database import connect_to_database
from src.create_tables import create_tables
from src.delete_tables import delete_tables


if __name__ == "__main__":
    conn = connect_to_database()
    delete_tables(conn)
    create_tables(conn)