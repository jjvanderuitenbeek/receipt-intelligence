import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import sys
from langchain_core.messages import HumanMessage
sys.path.append(str(Path().resolve()))

from src.receipt_intelligence.config import settings
from src.receipt_intelligence.modules.text2sql_service.graph import graph   

# --- Connect to the SQLite database ---
conn = sqlite3.connect(settings.DB_PATH)
cursor = conn.cursor()


# --- Streamlit app ---
st.set_page_config(page_title="Receipt Dashboard", layout="wide")
st.title("📊 Receipt Dashboard")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

state = None

# --- Conversational interface: User input message ---
# Text area for input
st.text_area(
    "Type your message:",
    key="user_input",
    height=100,
    placeholder="Type your message and press Enter or click Send..."
)

state = None


if st.button("Send") and st.session_state.user_input:
    
    state = graph.invoke(
        {"messages": [("user", st.session_state.user_input)]},
        config={"configurable": {"thread_id": "conversation-1"}},
        state=state,
    )

    # Display the response in a separate box
    st.subheader("Receipt Bot Response:")
    st.text_area("Response", value=state["final_response"], height=300)

# --- Sidebar: Query input ---
st.sidebar.header("Custom SQL Query")
user_query = st.sidebar.text_area("Enter SQL query:", value="SELECT * FROM receiptTable LIMIT 10")
if st.sidebar.button("Run Query"):
    try:
        query_result = pd.read_sql_query(user_query, conn)
        st.subheader("Query Results")
        st.dataframe(query_result)
    except Exception as e:
        st.error(f"Error: {e}")

# --- Basic statistics ---
st.header("📈 Basic Statistics")

# Total receipts
total_receipts = pd.read_sql_query("SELECT COUNT(*) AS total FROM receiptTable", conn).iloc[0, 0]

# Total revenue
total_revenue = pd.read_sql_query("SELECT SUM(price_total) AS revenue FROM receiptTable", conn).iloc[0, 0]

# Total products sold
total_products = pd.read_sql_query("SELECT SUM(quantity) AS total_quantity FROM receiptTable", conn).iloc[0, 0]

# Number of unique stores
unique_stores = pd.read_sql_query("SELECT COUNT(DISTINCT store_cod) AS store_count FROM receiptTable", conn).iloc[0, 0]

# Show stats in columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Receipts", total_receipts)
col2.metric("Total Revenue", f"${total_revenue:,.2f}")
col3.metric("Total Products Sold", total_products)
col4.metric("Unique Stores", unique_stores)

# --- Data preview ---
st.header("🗂 Receipt Table Preview")
preview_df = pd.read_sql_query("SELECT * FROM receiptTable ORDER BY receipt_date DESC LIMIT 20", conn)
st.dataframe(preview_df)

# --- Close connection on app exit ---
conn.close()