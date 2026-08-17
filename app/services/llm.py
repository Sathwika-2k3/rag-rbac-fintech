from langchain_groq import ChatGroq

from app.config import GROQ_API_KEY

MODEL_NAME = "openai/gpt-oss-120b"


def get_llm() -> ChatGroq:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file — see .env.example."
        )
    return ChatGroq(model=MODEL_NAME, api_key=GROQ_API_KEY)
