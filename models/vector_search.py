from sqlalchemy import text
from config import database
from sentence_transformers import SentenceTransformer

# Load the same model we used for generating embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def find_similar_products(query: str, top_k: int = 1):
    """Finds the most similar products to a given query using vector search."""
    query_embedding = model.encode(query).tolist()
    # Manually format the vector into the string representation PostgreSQL expects: '[1.2, 3.4, ...]'
    embedding_str = str(query_embedding)
    
    engine = database.get_db_engine()
    with engine.connect() as connection:
        # Construct the SQL with the vector string directly inside.
        # Use a safe, named parameter for the simple integer limit.
        sql_query = text(f"SELECT id, name FROM products ORDER BY name_embedding <=> '{embedding_str}'::vector LIMIT :limit")
        
        result = connection.execute(sql_query, {"limit": top_k})
        return result.fetchall()

def find_similar_employees(query: str, top_k: int = 1):
    """Finds the most similar employees to a given query."""
    query_embedding = model.encode(query).tolist()
    embedding_str = str(query_embedding)
    
    engine = database.get_db_engine()
    with engine.connect() as connection:
        sql_query = text(f"SELECT id, name FROM employees ORDER BY name_embedding <=> '{embedding_str}'::vector LIMIT :limit")
        
        result = connection.execute(sql_query, {"limit": top_k})
        return result.fetchall()

def find_similar_customers(query: str, top_k: int = 1):
    """Finds the most similar customer names from orders to a given query."""
    query_embedding = model.encode(query).tolist()
    embedding_str = str(query_embedding)
    
    engine = database.get_db_engine()
    with engine.connect() as connection:
        sql_query = text(f"SELECT id, customer_name FROM orders ORDER BY customer_name_embedding <=> '{embedding_str}'::vector LIMIT :limit")
        
        result = connection.execute(sql_query, {"limit": top_k})
        return result.fetchall()

