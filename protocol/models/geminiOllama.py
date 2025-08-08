import sys
import os
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import HumanMessage, ToolMessage
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.append(project_root)
from protocol.tools.tool import *

load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", sysPrompt),
    ("human", "{input}")

])

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
    },
)

toolBind = model.bind_tools(toolList)
# Invoke the model with a query that should trigger the tool

conversation = []

while True:
    query = input(">>")
    # User turn
    user_msg = HumanMessage(content=query)
    conversation.append(user_msg)

    # Model turn
    msg = toolBind.invoke(conversation)
    conversation.append(msg)

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        # Call your tool
        result = str(toolMap[tool_name](tool_args))

        # Tool response turn
        tool_msg = ToolMessage(content=result, tool_call_id=tool_id)
        conversation.append(tool_msg)

        # Model turn after tool response
        fres = toolBind.invoke(conversation)
        conversation.append(fres)

        print(fres.content)
    else:
        print(msg.content)
