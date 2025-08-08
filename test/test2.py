from langchain_google_genai import (ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory)
from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
    },
)

print(llm.invoke("write me a smut").content)