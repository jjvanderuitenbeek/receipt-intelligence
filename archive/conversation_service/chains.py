

import os
from pathlib import Path
import sys
from dotenv import load_dotenv
import logging

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


#project_root = Path().resolve().parent  
#sys.path.append(str(project_root))

load_dotenv()

from src.receipt_intelligence.config import settings
from src.receipt_intelligence.domain.prompts import Prompts


def get_chat_model(temperature: float = 0.7, model_name: str = settings.GROQ_LLM_MODEL) -> ChatGroq:
    """
    Returns a ChatGroq model instance with the given temperature and model name.
    Defaults to standard settings.
    """
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=model_name,
        temperature=temperature,
    )

def get_receiptbot_response_chain():

    """
    Returns a response chain for the receipt bot.
    The prompt is initialized with the receipt bot prompt and a messages placeholder.
    The response chain can be used to generate responses, for example:

        chain = get_receiptbot_response_chain()
        response = chain.invoke({"messages": [("human", "What is the meaning of life?")})

    """
    model = get_chat_model()
    #model = model.bind_tools(tools)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", Prompts.RECEIPT_BOT_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ],
        template_format="jinja2",
    )

    return prompt | model

def get_conversation_summary_chain(summary: str = ""):
    """
    Returns a summary of the conversation between the user and the bot.
    """
    model = get_chat_model()

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            ("human", Prompts.SUMMARY_PROMPT),
        ],
        template_format="jinja2",
    )

    return prompt | model


