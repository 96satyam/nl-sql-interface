import openai
import json
from config import settings
from utils import helpers
from models import sql_validator, vector_search

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

def _get_entity_from_query(query: str):
    """
    Uses an LLM to identify a fuzzy product name from the user's query.
    Returns the entity name or None.
    """
    prompt = f"""
    You are an expert at extracting product names from user questions.
    Analyze the following user question and extract the most likely product name.
    
    Return your answer in a JSON object with a single key "product_name".
    If no specific product name is found, the value should be null.

    User Question: "{query}"
    
    JSON Response:
    """
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    
    result = json.loads(response.choices[0].message.content)
    return result.get("product_name")


def process_natural_language_query(query: str):
    """
    Takes a natural language query and converts it to a validated SQL query
    using a hybrid search approach.
    """
    print(f"Received query: '{query}'")

    # Step 1: Check for fuzzy product entities in the query
    product_name_entity = _get_entity_from_query(query)
    
    if product_name_entity:
        print(f"Fuzzy entity found: '{product_name_entity}'. Performing vector search...")
        
        # Step 2: If an entity is found, use vector search to find the exact product
        similar_products = vector_search.find_similar_products(product_name_entity)
        
        if not similar_products:
            return "Error: Could not find a matching product for your query."
            
        # Get the ID and name of the top match
        product_id, product_name = similar_products[0]
        print(f"Vector search identified best match: ID={product_id}, Name='{product_name}'")
        
        # Step 3: Enrich the prompt with the precise product ID
        enriched_query = f"{query} (specifically for product with id {product_id})"
    else:
        # If no entity, use the original query
        enriched_query = query

    # Step 4: Generate the final SQL query using the (potentially enriched) query
    schema = helpers.get_schema_definition()
    prompt = f"""
    ### Instructions
    You are an expert PostgreSQL assistant... (prompt continues as before)

    ### Database Schema
    {schema}

    ### User's Question
    {enriched_query}

    ### SQL Query
    """
    
    # ... The rest of the function (API call, validation, sanitization) remains the same
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a PostgreSQL expert..."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=500
        )
        raw_response = response.choices[0].message.content.strip()
        print(f"--- OpenAI Raw Response ---\n{raw_response}") # Let's print the raw response to see
        
        # --- NEW: Use the helper to extract only the SQL ---
        sql_query = helpers.extract_sql_from_response(raw_response)
        
        print(f"--- Extracted SQL ---\n{sql_query}")
        
        if not sql_validator.is_query_safe(sql_query):
            return "Error: The generated query is not safe to execute."
        
        safe_sql_query = sql_validator.sanitize_and_limit_query(sql_query)
        return safe_sql_query
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"Error: {e}"