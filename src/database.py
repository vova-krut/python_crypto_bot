import psycopg2
from dotenv import load_dotenv
import os


def connect_to_database():
    """
    #TODO write docs
    """
    load_dotenv()
    db_name = os.getenv("PG_DBNAME", None)
    db_user = os.getenv("PG_USER", None)
    db_password = os.getenv("PG_PASSWORD", None)
    db_host = os.getenv("PG_HOST", "localhost")
    db_port = os.getenv("PG_PORT", 5432)
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    conn.autocommit = True
    return conn
