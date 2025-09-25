import openai
import json
from sqlalchemy import text
from config import settings
from utils import helpers
from models import sql_validator, vector_search

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

def _extract_entities_from_query(query: str):
    """
    Uses an LLM to identify fuzzy entities (product, employee, or customer names)
    from the user's query.
    """
    prompt = f"""
    You are an expert at extracting entities from user questions.
    Analyze the user question and extract any product names, employee names, or customer names.
    
    Return a JSON object with keys "product_name", "employee_name", and "customer_name".
    If an entity is not found, its value should be null.

    User Question: "{query}"
    
    JSON Response:
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {}

def process_natural_language_query(query: str):
    """
    Takes a natural language query and converts it to a validated SQL query
    using a true hybrid search approach.
    """
    print(f"Received query: '{query}'")
    enriched_query = query
    
    entities = _extract_entities_from_query(query)
    
    if entities.get("employee_name"):
        entity = entities["employee_name"]
        print(f"Fuzzy employee entity found: '{entity}'. Performing vector search...")
        similar_items = vector_search.find_similar_employees(entity)
        if similar_items:
            item_id, item_name = similar_items[0]
            enriched_query = f"{query} (clarification: use employee with id {item_id} whose name is '{item_name}')"
    
    elif entities.get("product_name"):
        entity = entities["product_name"]
        print(f"Fuzzy product entity found: '{entity}'. Performing vector search...")
        similar_items = vector_search.find_similar_products(entity)
        if similar_items:
            item_id, item_name = similar_items[0]
            enriched_query = f"{query} (clarification: use product with id {item_id} whose name is '{item_name}')"

    elif entities.get("customer_name"):
        entity = entities["customer_name"]
        print(f"Fuzzy customer entity found: '{entity}'. Performing vector search...")
        similar_items = vector_search.find_similar_customers(entity)
        if similar_items:
            item_id, item_name = similar_items[0]
            enriched_query = f"{query} (clarification: use order involving customer '{item_name}' with order id {item_id})"

    print(f"Enriched query for SQL generation: '{enriched_query}'")

    schema = helpers.get_schema_definition()
    prompt = f"""
    ### Instructions
    You are an expert PostgreSQL assistant. Your task is to translate the user's question into a valid and secure PostgreSQL query.
    - You MUST only output the SQL query. Do not include any other text, explanations, or markdown formatting.
    - Do NOT allow any queries that modify the database, such as INSERT, UPDATE, DELETE, DROP, etc.
    - Ensure the query is secure and does not contain any vulnerabilities.
    - **IMPORTANT: Treat each question as a new, standalone query. Do not use context from previous questions.**

    ### Database Schema
    Here is the schema of the database you are working with:
    {schema}

    ### User's Question
    {enriched_query}

    ### SQL Query
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a PostgreSQL expert that translates natural language to SQL."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=500
        )
        raw_response = response.choices[0].message.content.strip()
        sql_query = helpers.extract_sql_from_response(raw_response)
        
        if not sql_validator.is_query_safe(sql_query):
            return "Error: The generated query is not safe to execute."
        
        return sql_validator.sanitize_and_limit_query(sql_query)
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

