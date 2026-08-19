import json

from app.services.llm import get_llm

JUDGE_PROMPT = """You are grading an AI assistant's answer for an internal company chatbot.

Question: {question}

Context the assistant was given:
{context}

Assistant's answer:
{answer}

Score the answer from 1 (worst) to 5 (best) on two dimensions:
- groundedness: does the answer only use facts present in the context, without inventing anything?
- relevance: does the answer actually address the question asked?

Respond with ONLY a JSON object and nothing else, in exactly this shape:
{{"groundedness": <1-5>, "relevance": <1-5>, "reasoning": "<one short sentence>"}}"""


def judge(question: str, context: str, answer: str) -> dict:
    response = get_llm().invoke(JUDGE_PROMPT.format(question=question, context=context, answer=answer))
    text = response.content.strip().strip("`").removeprefix("json").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"groundedness": None, "relevance": None, "reasoning": f"could not parse judge output: {text!r}"}
