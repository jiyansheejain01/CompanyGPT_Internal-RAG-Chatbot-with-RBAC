from dotenv import load_dotenv
import os

load_dotenv()


def setup_langsmith():
    api_key = os.getenv("LANGCHAIN_API_KEY")
    project = os.getenv("LANGCHAIN_PROJECT", "atliq-rag")
    tracing = os.getenv("LANGCHAIN_TRACING_V2", "false")

    if api_key and tracing == "true":
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = api_key
        os.environ["LANGCHAIN_PROJECT"] = project
        print(f"LangSmith tracing enabled — project: {project}")
    else:
        print("LangSmith tracing disabled — set LANGCHAIN_API_KEY and LANGCHAIN_TRACING_V2=true to enable")
