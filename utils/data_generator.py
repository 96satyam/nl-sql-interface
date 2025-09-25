import psycopg2
from faker import Faker
import random
import os
from dotenv import load_dotenv
load_dotenv()
# --- DATABASE CONNECTION DETAILS ---
# Make sure your Docker container is running before executing this script.
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# --- DATA GENERATION SETUP ---
fake = Faker()
NUM_DEPARTMENTS = 5
NUM_EMPLOYEES = 50
NUM_PRODUCTS = 100
NUM_ORDERS = 200

def populate_data():
    """Connects to the database and populates it with fake data."""
    conn = None
    try:
        # Establish the connection
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        print("Database connection established.")

        # --- 1. POPULATE DEPARTMENTS ---
        print("Populating departments...")
        departments = ['Engineering', 'Human Resources', 'Sales', 'Marketing', 'Support']
        for dept_name in departments:
            cur.execute("INSERT INTO departments (name) VALUES (%s) RETURNING id", (dept_name,))
        print(f"{len(departments)} departments populated.")

        # --- 2. POPULATE EMPLOYEES ---
        print("Populating employees...")
        for _ in range(NUM_EMPLOYEES):
            cur.execute(
                "INSERT INTO employees (name, department_id, email, salary) VALUES (%s, %s, %s, %s)",
                (fake.name(), random.randint(1, NUM_DEPARTMENTS), fake.email(), random.randint(40000, 150000))
            )
        print(f"{NUM_EMPLOYEES} employees populated.")

        # --- 3. POPULATE PRODUCTS ---
        print("Populating products...")
        for _ in range(NUM_PRODUCTS):
            cur.execute(
                "INSERT INTO products (name, price) VALUES (%s, %s)",
                (fake.catch_phrase(), round(random.uniform(10.0, 1000.0), 2))
            )
        print(f"{NUM_PRODUCTS} products populated.")

        # --- 4. POPULATE ORDERS ---
        print("Populating orders...")
        for _ in range(NUM_ORDERS):
            cur.execute(
                "INSERT INTO orders (customer_name, employee_id, order_total, order_date) VALUES (%s, %s, %s, %s)",
                (fake.name(), random.randint(1, NUM_EMPLOYEES), round(random.uniform(50.0, 5000.0), 2), fake.date_this_decade())
            )
        print(f"{NUM_ORDERS} orders populated.")

        # Commit the changes to the database
        conn.commit()
        print("\nData generation complete. Changes have been committed.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback() # Roll back the transaction on error
    finally:
        # Close the connection
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    populate_data()