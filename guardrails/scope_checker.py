from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

SCOPE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a query classifier for an internal company chatbot.
Your job is to determine if a question is relevant to company business operations.

Relevant topics include:
- HR policies, employee data, payroll, leave policies
- Financial reports, budgets, expenses
- Marketing campaigns, reports, strategies
- Engineering documentation, technical specs
- General company policies and handbooks

Irrelevant topics include:
- General knowledge questions unrelated to the company
- Personal advice, entertainment, jokes
- Coding help unrelated to company work
- News, sports, politics

Reply with ONLY one word: RELEVANT or IRRELEVANT"""),
    ("human", "Question: {query}")
])


def is_query_in_scope(query: str) -> tuple[bool, str]:
    try:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=10
        )
        chain = SCOPE_PROMPT | llm | StrOutputParser()
        result = chain.invoke({"query": query}).strip().upper()

        if "IRRELEVANT" in result:
            return False, "Your question is outside the scope of this company chatbot. Please ask questions related to company operations."
        return True, ""

    except Exception as e:
        # if scope check fails, allow the query through
        print(f"Scope check error: {e}")
        return True, ""


if __name__ == "__main__":
    test_queries = [
        "What is the employee leave policy?",
        "Who won the cricket match yesterday?",
        "What are the Q4 financial results?",
        "Tell me a joke"
    ]
    for q in test_queries:
        in_scope, msg = is_query_in_scope(q)
        print(f"Query    : {q}")
        print(f"In scope : {in_scope}")
        if msg:
            print(f"Message  : {msg}")
        print()
