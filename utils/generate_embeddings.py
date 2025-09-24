import psycopg2
from sentence_transformers import SentenceTransformer

# --- DATABASE CONNECTION DETAILS ---
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "admin" # <-- Use the password you set for your container
DB_HOST = "localhost"
DB_PORT = "5432"

# --- EMBEDDING MODEL SETUP ---
# This line downloads a pre-trained model.
# The first time you run this, it will take a few minutes to download.
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

def generate_and_store_embeddings():
    """Fetches data, generates embeddings, and stores them in the database."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        print("Database connection established.")

        # --- TABLES TO PROCESS ---
        tables_to_process = {
            "products": ("name", "name_embedding"),
            "employees": ("name", "name_embedding"),
            "orders": ("customer_name", "customer_name_embedding")
        }

        for table_name, (text_col, embedding_col) in tables_to_process.items():
            print(f"\n--- Processing table: {table_name} ---")

            # 1. Fetch records that don't have an embedding yet
            cur.execute(f"SELECT id, {text_col} FROM {table_name} WHERE {embedding_col} IS NULL")
            records = cur.fetchall()

            if not records:
                print(f"No new records to embed in {table_name}.")
                continue

            print(f"Found {len(records)} records to embed.")
            
            # Extract IDs and texts for batch processing
            ids = [rec[0] for rec in records]
            texts = [rec[1] for rec in records]

            # 2. Generate embeddings in a batch (much more efficient)
            print("Generating embeddings...")
            embeddings = model.encode(texts, show_progress_bar=True)

            # 3. Update the database with the new embeddings
            print("Updating database with embeddings...")
            for i, record_id in enumerate(ids):
                embedding = embeddings[i].tolist() # Convert numpy array to list
                cur.execute(
                    f"UPDATE {table_name} SET {embedding_col} = %s WHERE id = %s",
                    (embedding, record_id)
                )
            
            print(f"Successfully updated {len(ids)} records in {table_name}.")

        # Commit all changes
        conn.commit()
        print("\nAll embeddings generated and stored successfully.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    generate_and_store_embeddings()