from typing import Optional
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv
import cv2 as cv

load_dotenv()

# Define the tool
@tool(description="Get the current weather in a given location")
def get_weather(location: str) -> str:
    return f"It's sunny in {location}"

@tool(description="Opens the camera")
def cameraOn(portNum: Optional[int] = 0):
        cam = cv.VideoCapture(portNum)
        while True:
            _, ctx = cam.read()
            cv.imshow("cameraWindow", ctx)
            if(cv.waitKey(1) & 0xFF == ord("q")):
                break
        return "done"

# Initialize the model and bind the tool
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
llm_with_tools = llm.bind_tools([get_weather, cameraOn])

# Invoke the model with a query that should trigger the tool
query = "what is the weatbher in sanfansico"
msg = llm_with_tools.invoke(query)

# Check the tool calls in the response
print(msg)

#tool
if msg.tool_calls:
    tool_call = msg.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_id = tool_call["id"]

    toolMap = {
         "get_weather": get_weather,
         "cameraOn": cameraOn
    }

    result = toolMap[tool_name](tool_args)

    toolMsg = ToolMessage(content=result, tool_call_id = tool_id)
    fres = llm_with_tools.invoke([msg, toolMsg])
    print(fres)