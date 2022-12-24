from src.sql_queries import create_queries


def create_tables(conn) -> None:
    """
    #TODO write docs
    """
    cursor = conn.cursor()
    for query in create_queries:
        try:
            print(f"Execute: \n{query}")
            cursor.execute(query)
        except Exception as e:
            print(f"Failed to create table: \n{e}.")
        else:
            print(f"Succesfuly created table.")
    