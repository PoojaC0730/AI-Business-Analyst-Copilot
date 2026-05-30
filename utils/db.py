import os
import sqlite3
import pandas as pd
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "sales.db")

def execute_sql(sql: str, params: dict = None, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Executes a SQL query against the SQLite database with optional parameters and returns a Pandas DataFrame.
    """
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    finally:
        conn.close()
