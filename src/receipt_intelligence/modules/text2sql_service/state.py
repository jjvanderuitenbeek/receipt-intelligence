

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class ConversationState(TypedDict):
    """
    State class for the LangGraph workflow. 
    It keeps track of the information necessary to maintain a coherent conversation between the user and the bot.
    The StateGraph's state is defined as a typed dictionary containing an append-only list of messages. These messages form the chat history.

    Attributes:
        messages: A list of messages between the user and the bot.
        last_userquery_type (str): Current message type, used for routing the message to the correct node.
        final_response (str): The final response from the bot that is presented to the user    
    """
    messages: Annotated[list, add_messages]
    last_userquery_type: Literal["general_prompt", "sql_prompt"] | None
    final_response: str