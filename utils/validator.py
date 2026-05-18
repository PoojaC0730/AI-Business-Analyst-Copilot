import re

def is_safe_sql(sql: str) -> bool:
    """
    Validates that a SQL query only contains safe, read-only operations.
    """
    sql_upper = sql.upper()
    
    # Strictly reject modifying operations
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    for word in forbidden:
        if re.search(rf'\b{word}\b', sql_upper):
            return False
            
    # Ensure it's a valid SELECT or WITH statement
    if not (re.search(r'\bSELECT\b', sql_upper) or re.search(r'\bWITH\b', sql_upper)):
        return False
        
    return True
