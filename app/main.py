from fastapi import FastAPI, Depends

from app.services.auth import authenticate
from app.services.rag import answer_question

app = FastAPI()


# Login endpoint
@app.get("/login")
def login(user=Depends(authenticate)):
    return {"message": f"Welcome {user['username']}!", "role": user["role"]}


# Protected test endpoint
@app.get("/test")
def test(user=Depends(authenticate)):
    return {"message": f"Hello {user['username']}! You can now chat.", "role": user["role"]}


# Protected chat endpoint
@app.post("/chat")
def query(user=Depends(authenticate), message: str = "Hello"):
    result = answer_question(user["role"], message)
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "role": user["role"],
        "blocked": result["blocked"],
    }