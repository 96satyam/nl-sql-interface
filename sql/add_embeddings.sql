-- Add vector columns to store the embeddings

ALTER TABLE employees
ADD COLUMN name_embedding VECTOR(384);

ALTER TABLE products
ADD COLUMN name_embedding VECTOR(384);

ALTER TABLE orders
ADD COLUMN customer_name_embedding VECTOR(384);

-- Optional: Create indexes on these new columns for much faster searching later
CREATE INDEX idx_employees_name_embedding ON employees USING hnsw (name_embedding vector_l2_ops);
CREATE INDEX idx_products_name_embedding ON products USING hnsw (name_embedding vector_l2_ops);
CREATE INDEX idx_orders_customer_name_embedding ON orders USING hnsw (customer_name_embedding vector_l2_ops);