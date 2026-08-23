import sys
import time

from langchain_core.prompts import ChatPromptTemplate

from app.services.guardrails import check_input, check_output
from app.services.ingest import get_vectorstore
from app.services.llm import get_llm
from app.services.monitoring import log_usage
from app.services.rbac import allowed_departments, search_for_role

SYSTEM_PROMPT = """You are FinSolve's internal assistant. Answer the user's question using ONLY the context below.
If the context doesn't contain the answer, say plainly that you don't have access to that information — never guess or use outside knowledge.
Format your answer in clean Markdown (bold, bullet lists, and tables where helpful) — never use raw HTML tags such as <br>.

Context:
{context}"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ]
)


def format_context(documents) -> str:
    blocks = [f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}" for doc in documents]
    return "\n\n".join(blocks)


def answer_question(role: str, question: str, k: int = 4) -> dict:
    block_reason = check_input(question)
    if block_reason:
        return {"answer": block_reason, "sources": [], "blocked": True, "context": ""}

    documents = search_for_role(get_vectorstore(), role, question, k=k)
    if not documents:
        return {
            "answer": "I don't have access to any information that answers this question.",
            "sources": [],
            "blocked": False,
            "context": "",
        }

    context = format_context(documents)
    chain = prompt | get_llm()
    start = time.perf_counter()
    response = chain.invoke({"context": context, "question": question})
    latency_seconds = time.perf_counter() - start

    usage = getattr(response, "usage_metadata", None) or {}
    log_usage(
        role=role,
        question=question,
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        latency_seconds=latency_seconds,
    )

    sources = sorted({doc.metadata.get("source", "unknown") for doc in documents})
    answer = check_output(response.content, allowed_departments(role))
    return {"answer": answer, "sources": sources, "blocked": False, "context": context}


if __name__ == "__main__":
    role_arg = sys.argv[1] if len(sys.argv) > 1 else "hr"
    question_arg = sys.argv[2] if len(sys.argv) > 2 else "What is the leave policy?"
    result = answer_question(role_arg, question_arg)
    print(result["answer"])
    print("\nSources:", ", ".join(result["sources"]) or "none")
