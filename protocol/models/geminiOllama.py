from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # oth
    )
messages = [
    (
        "system",
        "You are a helpful assistant that does some spicy story telling",
    ),
    ("human", "tell me a story."),
]

def save(bruh):
    pass 

def defaultMessage(message):
    print(llm.invoke(message).content)

def streamMessage(message):
    for chunk in llm.stream(message.content):
        print(chunk.content)