import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

from rag.chain import run_rag_chain, ensure_ingestion
from ingestion.embedder import get_embedding_model
from retrieval.qdrant_store import search_documents
from auth.rbac import get_allowed_departments


def get_ragas_llm():
    return LangchainLLMWrapper(ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",
        temperature=0
    ))


def get_ragas_embeddings():
    return LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    ))


def build_eval_dataset() -> Dataset:
    ensure_ingestion()
    embedding_model = get_embedding_model()

    with open("evaluation/test_dataset.json") as f:
        test_cases = json.load(f)

    questions, answers, contexts, ground_truths = [], [], [], []

    for case in test_cases:
        print(f"Running: {case['question']}")
        result = run_rag_chain(query=case["question"], role=case["role"])

        allowed_depts = get_allowed_departments(case["role"])
        query_embedding = embedding_model.encode(case["question"]).tolist()
        retrieved = search_documents(query_embedding, allowed_depts, top_k=5)

        questions.append(case["question"])
        answers.append(result["answer"])
        contexts.append([doc.page_content for doc in retrieved])
        ground_truths.append(case["ground_truth"])

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })


def run_evaluation():
    print("=" * 50)
    print("Building eval dataset...")
    print("=" * 50)
    dataset = build_eval_dataset()

    # configure ragas to use groq + local embeddings
    ragas_llm = get_ragas_llm()
    ragas_embeddings = get_ragas_embeddings()

    metrics = [faithfulness, answer_relevancy, context_recall]
    for metric in metrics:
        metric.llm = ragas_llm
        if hasattr(metric, "embeddings"):
            metric.embeddings = ragas_embeddings

    print("\nRunning RAGAS evaluation...")
    try:
        results = evaluate(
            dataset=dataset,
            metrics=metrics
        )
    except Exception as e:
        print(f"RAGAS evaluation error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 50)
    print("EVALUATION RESULTS")
    print("=" * 50)
    df = results.to_pandas()

    # print actual columns available
    print(f"Columns: {df.columns.tolist()}")
    print(df.to_string())

    # safe average printing
    print("\nAverage scores:")
    for col in df.columns:
        try:
            avg = df[col].mean()
            if avg == avg:  # skip NaN
                print(f"  {col}: {avg:.3f}")
        except:
            pass

    df.to_csv("evaluation/eval_results.csv", index=False)
    print("\nResults saved to evaluation/eval_results.csv")


if __name__ == "__main__":
    run_evaluation()
