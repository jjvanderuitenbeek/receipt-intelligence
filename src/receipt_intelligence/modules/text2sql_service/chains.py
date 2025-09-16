

import os
from dotenv import load_dotenv
import logging

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

from src.receipt_intelligence.config import settings



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

def get_response_chain():
    """
    Returns a runnable pipeline to generate responses from a system message and a list of messages.
    The response chain can be used to generate responses, for example:
        chain = get_response_chain()
        response = chain.invoke({"system_message": "Your task is to ...", "msgs": [("human", "What is the meaning of life?")})
    """
    model = get_chat_model()
    #model = model.bind_tools(tools)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_message}"),
            MessagesPlaceholder(variable_name="msgs"),
        ]
    )

    return prompt | model

