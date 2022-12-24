from src.sql_queries import delete_queries


def delete_tables(conn) -> None:
    """
    #TODO write docs
    """
    cursor = conn.cursor()
    for query in delete_queries:
        try:
            print(f"Execute: \n{query}")
            cursor.execute(query)
        except Exception as e:
            print(f"Failed to delete table: \n{e}.")
        else:
            print(f"Succesfuly deleted table.")
    