

from dotenv import load_dotenv
import logging

from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

from src.receipt_intelligence.config import settings
from .prompts import Prompts

from .chains import get_response_chain
from .state import ConversationState


def classify_message_node(state: ConversationState): 
    """
    Runs the classify message node.
    This node takes a langchain MessagesState
    The last message in the messages list is classified as either "receipt_prompt" or "general_prompt".
    The node runs the get_response_chain() chain and passes the state to it. 
    The response is then returned as a dictionary with a single key "messages" containing the response.
    """
    last_message = state["messages"][-1].content

    response_chain = get_response_chain()

    response = response_chain.invoke({"system_message": Prompts.CLASSIFY_MESSAGE_PROMPT, "msgs": [HumanMessage(content=last_message)]})

    return {"last_userquery_type": response.content}


def explain_bot_purpose_node(state: ConversationState):

    return {"final_response": Prompts.EXPLAIN_BOT_PURPOSE_PROMPT}

def generate_sqlquery_node(state: ConversationState):

    last_message = state["messages"][-1].content
   
    response_chain = get_response_chain()

    response = response_chain.invoke({"system_message": Prompts.GENERATE_SQLQUERY_PROMPT, "msgs": [HumanMessage(content=last_message)]})

    return {"final_response": response.content}
