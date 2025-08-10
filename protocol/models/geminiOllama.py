# protocol/models/geminiOllama.py
import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import HumanMessage, ToolMessage
from langchain.prompts import ChatPromptTemplate

# Import tools dynamically
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.append(project_root)
from protocol.tools.tool import sysPrompt, toolList, toolMap

load_dotenv()

# Store conversation state
conversation = []
toolBind = None


def init_gemini():
    """Initialize Gemini model + tools."""
    global toolBind

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


async def run_gemini_async(user_input: str) -> str:
    """
    Runs a single Gemini query asynchronously.
    :param user_input: User's query
    :param mode: Optional mode for prompt styling
    """
    global conversation, toolBind

    if toolBind is None:
        init_gemini()

    # Add user message
    user_msg = HumanMessage(content=user_input)
    conversation.append(user_msg)

    # Model turn
    msg = toolBind.invoke(conversation)
    conversation.append(msg)

    # Handle tool calls
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        # Call the tool
        result = str(toolMap[tool_name](tool_args))

        # Tool response
        tool_msg = ToolMessage(content=result, tool_call_id=tool_id)
        conversation.append(tool_msg)

        # Final model response after tool output
        fres = toolBind.invoke(conversation)
        conversation.append(fres)
        return fres.content
    else:
        return msg.content
