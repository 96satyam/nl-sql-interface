# Natural Language Search Interface for PostgreSQL 🤖

An intelligent, conversational interface that empowers users to query a PostgreSQL database using plain English. This project leverages a Large Language Model (LLM) to translate natural language into secure, executable SQL, featuring a hybrid search system for both precise and fuzzy matching.

## 🌟 Features

*   **Natural Language to SQL**: Ask complex questions like "What is the average salary by department?" and receive immediate, accurate results from your database.
*   **Hybrid Search Engine**: Combines traditional SQL filtering with AI-powered vector search to handle fuzzy queries (e.g., finding "Jon Smyth" when the database has "John Smith").
*   **Security-First Design**: A robust validation and sanitization layer acts as a "gatekeeper" to inspect every AI-generated query, preventing destructive commands and overly complex queries to protect database integrity and performance.
*   **Interactive UI**: A clean, modern chat interface built with Streamlit that maintains a history of your conversation.
*   **Intelligent Data Visualization**: A "smart chart" feature that analyzes query results and automatically suggests the most appropriate visualization (e.g., bar chart for categorical data, line chart for time-series).
*   **Data Export**: Download any query result as a CSV file with a single click for offline analysis.

## ⚙️ How It Works

The application employs a sophisticated hybrid search strategy to provide accurate and secure results:

1.  **Entity Recognition**: When a user enters a query, the system first uses an LLM to quickly identify if a "fuzzy" entity (like a product name) is present.
2.  **Vector Search (Fuzzy Matching)**: If an entity is found, its name is converted into a vector embedding. The system then performs a similarity search against pre-calculated embeddings in the `pgvector` database to find the exact ID of the most likely match.
3.  **Enriched Prompt Engineering**: The original user query is then "enriched" with the precise ID found in the vector search step. This enriched query, along with the database schema, is sent to the primary LLM.
4.  **Secure SQL Generation**: The LLM translates the enriched query into a SQL statement.
5.  **Validation & Sanitization**: The generated SQL is rigorously checked against a denylist of forbidden keywords, validated for complexity (e.g., max number of `JOIN`s), and sanitized to ensure a `LIMIT` clause is present.
6.  **Data Retrieval & Display**: Only after passing all security checks is the SQL query executed against the database. The results are then displayed in the UI as an interactive table, with options for visualization and download.

## 🛠️ Technology Stack

| Category      | Technology                                                                                             |
| :------------ | :----------------------------------------------------------------------------------------------------- |
| Frontend      | Streamlit                                                                                              |
| Backend       | Python, OpenAI API                                                                                     |
| Database      | PostgreSQL with `pgvector` extension                                                                   |
| AI / ML       | OpenAI GPT-4o-mini (for NL-to-SQL), Sentence Transformers (`all-MiniLM-L6-v2`) (for vector embeddings) |
| Libraries     | `pandas`, `psycopg2`, `SQLAlchemy`, `Faker`, `python-dotenv`                                           |

## 📂 Project Structure

The project is organized in a modular structure to ensure maintainability and scalability:

```
nl-sql-interface/
├── app.py                 # Main Streamlit application entry point
├── config/
│   ├── database.py        # Handles database connection logic
│   └── settings.py        # Manages API keys and credentials loading
├── models/
│   ├── query_processor.py # Core logic for NL-to-SQL translation and hybrid search
│   ├── vector_search.py   # Functions for vector similarity search
│   └── sql_validator.py   # Implements security validation and sanitization for SQL queries
├── sql/
│   ├── schema.sql         # Defines the main database schema
│   └── add_embeddings.sql # Script to add vector columns to the database
├── utils/
│   ├── data_generator.py  # Populates the database with sample data
│   ├── generate_embeddings.py # Generates and stores AI embeddings for vector search
│   └── helpers.py         # Contains various utility functions
├── .env                   # Stores sensitive environment variables (not committed to Git)
├── requirements.txt       # Lists all Python dependencies
└── README.md              # Project overview and documentation
```

## 🚀 Local Setup and Installation

### Prerequisites

*   Git
*   Python 3.9+
*   Docker and Docker Compose

### Steps

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/YOUR_USERNAME/nl-sql-interface.git
    cd nl-sql-interface
    ```

2.  **Set Up the Database with Docker**
    The project uses a Docker container for PostgreSQL with the `pgvector` extension.

    ```bash
    docker run --name nl-search-db -e POSTGRES_PASSWORD=admin -p 5432:5432 -d pgvector/pgvector:pg16
    ```

3.  **Create a Virtual Environment**

    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

4.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Up Environment Variables**
    Create a file named `.env` in the project root and add your credentials:

    ```
    OPENAI_API_KEY="sk-..."
    DB_NAME=""
    DB_USER=""
    DB_PASSWORD=""
    DB_HOST="localhost"
    DB_PORT="5432"
    ```

6.  **Prepare and Populate the Database**
    Run the following scripts in order:

    ```bash
    # 1. Create the tables
    docker exec -i nl-search-db psql -U postgres < sql/schema.sql

    # 2. Add vector columns
    docker exec -i nl-search-db psql -U postgres < sql/add_embeddings.sql

    # 3. Populate with sample data
    python utils/data_generator.py

    # 4. Generate AI embeddings
    python utils/generate_embeddings.py
    ```

7.  **Run the Streamlit App**

    ```bash
    streamlit run app.py
    ```

    The application will open in your web browser.



## 📈 Future Improvements

*   **Advanced Visualizations**: Implement more chart types (e.g., pie charts, scatter plots) and allow users to select their preferred visualization.
*   **User Authentication**: Add a login system to support multiple users.
*   **Pagination**: Add front-end pagination for results to handle very large datasets gracefully.
*   **Query Caching**: Implement a caching layer to store the results of frequent queries, improving performance and reducing costs.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
