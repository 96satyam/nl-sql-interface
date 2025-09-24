import re
import streamlit as st
import pandas as pd


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


def display_intelligent_chart(df: pd.DataFrame):
    """
    Analyzes the DataFrame and displays the most appropriate chart.
    """
    st.write("---")
    st.markdown("#### Data Visualization")

    # Rule 1: Time-series data (Line Chart)
    # Check for a datetime column and at least one numeric column
    date_cols = df.select_dtypes(include=['datetime64']).columns
    numeric_cols = df.select_dtypes(include=['number']).columns

    if not date_cols.empty and not numeric_cols.empty:
        st.info("💡 Detected time-series data. Displaying a line chart.")
        st.line_chart(df.set_index(date_cols[0])[numeric_cols])
        return

    # Rule 2: Categorical vs. Numerical data (Bar Chart)
    # Check for exactly one string column and at least one numeric column
    string_cols = df.select_dtypes(include=['object', 'string']).columns
    if len(string_cols) == 1 and not numeric_cols.empty:
        st.info("💡 Detected categorical data. Displaying a bar chart.")
        st.bar_chart(df.set_index(string_cols[0])[numeric_cols])
        return

    # Fallback message if no suitable chart type is found
    st.warning("Could not determine a suitable chart type for this data.")
