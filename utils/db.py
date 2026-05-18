import sqlite3
import pandas as pd

def execute_sql(sql: str, db_path: str = "sales.db") -> pd.DataFrame:
    """
    Executes a SQL query against the SQLite database and returns a Pandas DataFrame.
    """
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()
