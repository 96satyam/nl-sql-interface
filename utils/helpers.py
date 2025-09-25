import re
import streamlit as st
import pandas as pd
import openai
import json


def get_schema_definition():
    """Reads the database schema from the SQL file."""
    try:
        with open('sql/schema.sql', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: Could not find schema.sql file."

def extract_sql_from_response(response_text: str):
    """
    Extracts the SQL query from a response that might include markdown.
    """
    # Regex to find code block between ```sql and ```
    match = re.search(r"```sql\s*(.*?)\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no markdown block, assume the whole response is the query
    return response_text.strip()


def get_ai_chart_recommendation(df: pd.DataFrame, user_question: str):
    """
    Asks an LLM to recommend the best chart type and columns for the given data.
    """
    # Get a summary of the dataframe to send to the AI
    df_summary = df.head().to_string()
    
    prompt = f"""
    You are an expert data visualization assistant. Your task is to recommend the best chart to visualize the user's query results.
    
    The user asked: "{user_question}"
    
    The resulting data is:
    {df_summary}
    
    Analyze the user's intent and the data's structure. Recommend the best chart type from the following options: 'bar', 'line', 'pie', 'scatter', 'none'.
    
    Return your answer as a JSON object with the following keys:
    - "chart_type": (e.g., "bar")
    - "x_column": The column to use for the x-axis.
    - "y_column": The column or columns to use for the y-axis (can be a list of strings).
    - "title": A descriptive title for the chart.
    
    If no chart is suitable, set "chart_type" to "none".

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
    except Exception as e:
        print(f"Error getting chart recommendation: {e}")
        return {"chart_type": "none"}

# --- UPDATED: Main Chart Display Function ---
def display_intelligent_chart(df: pd.DataFrame, user_question: str):
    """
    Gets an AI recommendation and displays the most appropriate chart.
    """
    st.write("---")
    st.markdown("#### Data Visualization")

    recommendation = get_ai_chart_recommendation(df, user_question)
    chart_type = recommendation.get("chart_type")
    x_col = recommendation.get("x_column")
    y_col = recommendation.get("y_column")
    title = recommendation.get("title")

    if chart_type == 'none' or not x_col or not y_col:
        st.warning("Could not determine a suitable chart type for this data.")
        return

    st.info(f"💡 AI Recommendation: A **{chart_type.replace('_', ' ')} chart** is best for this data.")
    st.subheader(title)

    try:
        # Set the index for charting
        chart_df = df.set_index(x_col)

        if chart_type == 'bar':
            st.bar_chart(chart_df[y_col])
        elif chart_type == 'line':
            st.line_chart(chart_df[y_col])
        elif chart_type == 'pie':
            st.pie_chart(chart_df[y_col])
        elif chart_type == 'scatter':
            st.scatter_chart(df, x=x_col, y=y_col)
    except Exception as e:
        st.error(f"Failed to create chart: {e}")
