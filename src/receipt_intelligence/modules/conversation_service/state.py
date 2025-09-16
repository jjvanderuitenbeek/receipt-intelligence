
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from typing import Annotated, Literal


class ConversationState(TypedDict):
    """
    State class for the LangGraph workflow. 
    It keeps track of the information necessary to maintain a coherent conversation between the user and the bot.

    Attributes:
        messages: A list of messages between the user and the bot.
        message_type (str): Current message type, used for routing the message to the correct node.
        summary (str): A summary of the conversation so far. This is used to reduce the token usage of the model.
    """

    messages: Annotated[list, add_messages]
    message_type: Literal["receipt_prompt", "general_prompt"]
    summary: str

