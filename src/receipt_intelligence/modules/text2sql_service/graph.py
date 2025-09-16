






from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from .state import ConversationState
from .nodes import classify_message_node, explain_bot_purpose_node, generate_sqlquery_node


def create_workflow_graph():

    graph_builder = StateGraph(ConversationState)

    # define nodes
    graph_builder.add_node("classify_message", classify_message_node)
    graph_builder.add_node("explain_bot_purpose", explain_bot_purpose_node)
    graph_builder.add_node("generate_sqlquery", generate_sqlquery_node)

    # define edges
    graph_builder.add_edge(START, "classify_message")
    graph_builder.add_conditional_edges(
        "classify_message",
        lambda state: state.get("last_userquery_type"),
        {"receipt_prompt": "generate_sqlquery", "general_prompt": "explain_bot_purpose"},
    )    
    graph_builder.add_edge("explain_bot_purpose", END)
    graph_builder.add_edge("generate_sqlquery", END)

    return graph_builder

# compile with checkpointer to retain memory
memory = InMemorySaver()
graph = create_workflow_graph().compile(checkpointer=memory)

# Write graph to png
from IPython.display import Image, display
img = graph.get_graph().draw_mermaid_png()
with open("static/graph.png", "wb") as f:
    f.write(img)
