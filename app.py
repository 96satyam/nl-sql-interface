import streamlit as st
import pandas as pd
from sqlalchemy import text
from config import database
from models import query_processor
from utils import helpers

# --- Helper function for CSV download ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NL-to-SQL", page_icon="🤖", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", width=200)
    st.subheader("About")
    st.write("""
        This application is a proof-of-concept for a Natural Language to SQL (NL-to-SQL) search interface. 
        It leverages a Large Language Model (LLM) to translate plain English questions into executable SQL queries 
        for a PostgreSQL database.
    """)
    st.write("---")
    st.subheader("Technology Stack")
    st.write("""
        - **Streamlit**: For the interactive web UI.
        - **OpenAI GPT-4o-mini**: For NL-to-SQL translation & chart recommendations.
        - **Sentence Transformers**: For creating vector embeddings.
        - **PostgreSQL with pgvector**: For hybrid search capabilities.
    """)

# --- MAIN PAGE ---
st.title("🤖 Natural Language Search for Your Database")
st.write("""
    Ask a question in plain English, and the system will translate it into a SQL query, 
    which will be used to retrieve data from the database.
""")
st.write("---")
st.markdown("#### Example Questions:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Who are the top 5 highest paid employees?"):
        st.session_state.user_question = "Who are the top 5 highest paid employees?"
with col2:
    if st.button("What is the average salary by department?"):
        st.session_state.user_question = "What is the average salary by department?"
with col3:
    if st.button("Show order totals by date for the last 10 orders"):
        st.session_state.user_question = "Show order totals by date for the last 10 orders"
st.write("---")

# --- SESSION STATE INITIALIZATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'latest_df' not in st.session_state:
    st.session_state.latest_df = None
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""
if 'chart_visible' not in st.session_state:
    st.session_state.chart_visible = False

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], pd.DataFrame):
            st.dataframe(message["content"])
        else:
            st.markdown(message["content"], unsafe_allow_html=True)

# Get user input
user_question_input = st.chat_input("Ask a question about your data...")
if user_question_input:
    st.session_state.user_question = user_question_input
    st.session_state.chart_visible = False # Hide old chart on new question

# Process the question if one exists
if st.session_state.user_question:
    st.session_state.messages.append({"role": "user", "content": st.session_state.user_question})
    with st.chat_message("user"):
        st.markdown(st.session_state.user_question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            sql_query = query_processor.process_natural_language_query(st.session_state.user_question)

            with st.expander("View Generated SQL"):
                st.code(sql_query, language="sql")
            
            if "error" in sql_query.lower():
                st.error(sql_query)
                st.session_state.messages.append({"role": "assistant", "content": sql_query})
            else:
                try:
                    engine = database.get_db_engine()
                    with engine.connect() as connection:
                        df = pd.read_sql_query(text(sql_query), connection)

                    st.success("Query executed successfully!")
                    
                    embedding_cols = [col for col in df.columns if 'embedding' in col]
                    df_display = df.drop(columns=embedding_cols)
                    
                    st.dataframe(df_display)
                    st.session_state.latest_df = df_display
                    st.session_state.messages.append({"role": "assistant", "content": df_display})

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
    
    # Store the question that generated the latest dataframe for context
    st.session_state.latest_query = st.session_state.user_question
    st.session_state.user_question = ""

# Display buttons and chart if there's a recent result
if st.session_state.latest_df is not None:
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        csv = convert_df_to_csv(st.session_state.latest_df)
        st.download_button(label="📥 Download as CSV", data=csv, file_name='query_results.csv', mime='text/csv')
    with col2:
        if st.button("📊 Build Chart"):
            st.session_state.chart_visible = not st.session_state.chart_visible

    if st.session_state.chart_visible:
        helpers.display_intelligent_chart(st.session_state.latest_df, st.session_state.latest_query)
