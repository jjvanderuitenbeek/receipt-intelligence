
from src.receipt_intelligence.modules.conversation_service.state import ConversationState
from src.receipt_intelligence.modules.conversation_service.graph import graph   

from langchain_core.messages import HumanMessage

import asyncio

async def run_chat(graph):
    state = {
        "messages": [],
        "message_type": "general_prompt",
        "summary": ""
    }

    while True:
        user_input = input("You: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"].append(HumanMessage(content=user_input))

        # Await the async graph call
        state = await graph.ainvoke(state)

        # Print bot response
        last_message = state["messages"][-1]
        print("Bot:", last_message.content)

# Run the async loop
asyncio.run(run_chat(graph))