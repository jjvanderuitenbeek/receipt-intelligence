
from src.receipt_intelligence.modules.text2sql_service.graph import graph   

# .venv\Scripts\activate.bat
# python chatbot.py

state = None

while True:
    user_input = input("Enter a message (or 'quit' to stop): ")
    if user_input.lower() == "quit":
        break

    # Run the graph with previous state
    state = graph.invoke(
        {"messages": [("user", user_input)]},
        config={"configurable": {"thread_id": "conversation-1"}},
        state=state,
    )

    print(state["final_response"])

    if state["last_userquery_type"] == "receipt_prompt":
        break