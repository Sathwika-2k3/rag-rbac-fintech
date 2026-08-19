from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.auth import authenticate
from app.services.monitoring import get_usage_report
from app.services.rag import answer_question
from app.services.rbac import allowed_departments

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Dev only — Vite can pick any port if its default is taken. Locked to a single
    # real origin before Milestone 14's deployment.
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Login endpoint
@app.get("/login")
def login(user=Depends(authenticate)):
    return {"message": f"Welcome {user['username']}!", "role": user["role"]}


# Protected test endpoint
@app.get("/test")
def test(user=Depends(authenticate)):
    return {"message": f"Hello {user['username']}! You can now chat.", "role": user["role"]}


# Who-am-I endpoint — lets the frontend show role + allowed departments after login
@app.get("/me")
def me(user=Depends(authenticate)):
    return {
        "username": user["username"],
        "role": user["role"],
        "allowed_departments": allowed_departments(user["role"]),
    }


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


# Token/cost usage report — company spend data, restricted to c-level
@app.get("/usage")
def usage(user=Depends(authenticate)):
    if user["role"] != "c-level":
        raise HTTPException(status_code=403, detail="Only c-level can view usage and cost data.")
    return get_usage_report()