
#https://github.com/techwithtim/LangGraph-Tutorial/blob/main/main.py

from langgraph.graph import END, START, StateGraph

from .state import ConversationState
from .nodes import introduction_node, summarize_conversation_node, classify_message_node, generate_sqlquery_node, route_conversation_node


def create_workflow_graph():

    

    graph_builder = StateGraph(ConversationState)

    # add nodes
    graph_builder.add_node("classifier_node", classify_message_node)
    graph_builder.add_node("route_conversation_node", route_conversation_node)
    graph_builder.add_node("introductory_conversation_node", introduction_node)
    graph_builder.add_node("generate_sqlquery_node", generate_sqlquery_node)

    #graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)
  

    # define flow (add edges)
    graph_builder.add_edge(START, "classifier_node")
    graph_builder.add_edge("classifier_node", "route_conversation_node")
    graph_builder.add_conditional_edges(
        "route_conversation_node",
        lambda state: state.get("next"),
        {"receipt_prompt": "generate_sqlquery_node", "general_prompt": "introductory_conversation_node"},
    )
    graph_builder.add_edge("introductory_conversation_node", END)
    graph_builder.add_edge("generate_sqlquery_node", END)


    return graph_builder

# Compiled without a checkpointer. Used for LangGraph Studio
graph = create_workflow_graph().compile()


from IPython.display import Image, display
img = graph.get_graph().draw_mermaid_png()
with open("static/graph.png", "wb") as f:
    f.write(img)
