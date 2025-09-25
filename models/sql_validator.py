# A list of keywords that are not allowed in the generated SQL
DENY_LIST = [
    "delete", "insert", "update", "drop", "alter", "truncate",
    "merge", "create", "grant", "revoke"
]

# a complexity limit
MAX_JOINS = 3

# a default result limit
DEFAULT_LIMIT = 100

def is_query_safe(sql_query: str) -> bool:
    """
    Validates a SQL query to ensure it's safe to execute.
    - Checks if the query starts with SELECT.
    - Checks for any forbidden keywords from the DENY_LIST.
    - Checks for an excessive number of JOINs.
    """
    query_lower = sql_query.lower()

    if not query_lower.strip().startswith("select"):
        print("Validation Failed: Query does not start with SELECT.")
        return False

    for keyword in DENY_LIST:
        if keyword in query_lower:
            print(f"Validation Failed: Query contains forbidden keyword '{keyword}'.")
            return False

    if query_lower.count("join") > MAX_JOINS:
        print(f"Validation Failed: Query exceeds the maximum of {MAX_JOINS} JOINs.")
        return False

    return True

def sanitize_and_limit_query(sql_query: str) -> str:
    """
    Sanitizes the query and ensures a LIMIT clause is present.
    """
    query = sql_query.strip()

    if query.endswith(';'):
        query = query[:-1]

    if "limit" not in query.lower():
        query = f"{query} LIMIT {DEFAULT_LIMIT}"
        print(f"Sanitization: No LIMIT clause found. Appending 'LIMIT {DEFAULT_LIMIT}'.")

    return query + ";"