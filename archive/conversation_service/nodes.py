from langchain_core.runnables import RunnableConfig
from langchain_core.messages import RemoveMessage

from src.receipt_intelligence.modules.conversation_service.state import ConversationState
from src.receipt_intelligence.modules.conversation_service.chains import get_receiptbot_response_chain, get_conversation_summary_chain, get_chat_model



def generate_sqlquery_node(state: ConversationState):

    model = get_chat_model()

    last_message = state["messages"][-2]

    prompt = [
            {
                "role": "system",
                "content": "You are an assistant that generates SQL queries. "
                "The database has a table named receiptTable with the following fields: "
                "- receipt_date (DATE) "
                "- store_cod (TEXT) "
                "- product (TEXT) "
                "- quantity (INTEGER) "
                "- price_unit (FLOAT) "
                "- price_total (FLOAT) "
                "- discount_ind (TEXT) → this field contains 'J' (yes) or 'N' (no) "

                "Instructions: "
                "- Always return a complete SQL query. "
                "- Use only the fields listed above. "
                "- Do not add extra columns or tables. "
                "- If the user question is ambiguous, make reasonable assumptions and state them as SQL comments (`--`). "
                "- Format the SQL with proper indentation and uppercase keywords. "
            },
            {
                "role": "user",
                "content": last_message.content
            }
        ]
    
    response = model.invoke(prompt)
    print(response.content)

    return{"messages": [{"role": "assistant", "content": response.content}]}



def route_conversation_node(state: ConversationState):

    last_message = state["messages"][-1]

    return {"next": last_message.content}
    
def classify_message_node(state: ConversationState):
    
    last_message = state["messages"][-1]
    model = get_chat_model()

    prompt = [
            {
                "role": "system",
                "content": "Classify the user message as either: "
                "'receipt_prompt': if the user asks a question directly related to receipt data"
                "'general_prompt': if the user asks about anything unrelated to the receipt data"
                "You can only output one of these: 'receipt_prompt' or 'general_prompt'"
            },
            {
                "role": "user",
                "content": last_message.content
            }
        ]

    response = model.invoke(prompt)

    return{"messages": [{"role": "assistant", "content": response.content}]}



async def introduction_node(state: ConversationState, config: RunnableConfig):
    """
    Runs the conversation introduction node.

    This node takes a langchain MessagesState, which is a typed dictionary containing the following fields:
        - messages: A list of messages, where each message is a dictionary containing the role and content of the message.
        - user_context: The context of the user.
        - user_name: The name of the user.
        - summary: A summary of the conversation.

    The node runs the get_receiptbot_response_chain() chain and passes the state to it. 
    The response is then returned as a dictionary with a single key "messages" containing the response.
    """

    # ConversationState is a typed dictionary with the following attributes: messages, user_context, user_name, summary
    summary = state.get("summary", "")
    user_name = state.get("user_name", "Jonathan")

    conversation_chain = get_receiptbot_response_chain()

    response = await conversation_chain.ainvoke(
        {
            "messages": state["messages"],
            "user_name": user_name,
            "summary": summary,
        },
        config,
    )
    
    return {"messages": response.content}



async def summarize_conversation_node(state: ConversationState):
    
    """
    Runs the summarize conversation node.
    This node takes a langchain MessagesState.
    The node runs the get_conversation_summary_chain() chain and passes the state to it.
    The messages are replaced by the summary
    """
    
    summary = state.get("summary", "")
    summary_chain = get_conversation_summary_chain(summary)

    response = await summary_chain.ainvoke(
        {
            "messages": state["messages"],
            "summary": summary,
        }
    )

    delete_messages = [
        RemoveMessage(id=m.id)
        for m in state["messages"][: -5]
    ]
    return {"summary": response.content, "messages": delete_messages}