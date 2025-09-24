from config import database
from sentence_transformers import SentenceTransformer

# Load the same model we used for generating embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def find_similar_products(query: str, top_k: int = 1):
    """
    Finds the most similar products to a given query using vector search.
    """
    # 1. Convert the user's query to an embedding
    query_embedding = model.encode(query)

    # 2. Search the database for the most similar vectors
    conn = database.get_db_connection()
    cur = conn.cursor()
    
    # The <=> operator from pgvector calculates the cosine distance between vectors
    cur.execute(
        """
        SELECT id, name FROM products
        ORDER BY name_embedding <=> %s::vector
        LIMIT %s
        """,
        (query_embedding.tolist(), top_k)
    )
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return results