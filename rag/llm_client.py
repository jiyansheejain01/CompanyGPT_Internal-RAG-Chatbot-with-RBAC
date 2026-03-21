from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()


def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",
        temperature=0.2,
        max_tokens=1024
    )
