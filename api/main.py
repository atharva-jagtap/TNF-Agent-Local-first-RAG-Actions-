from fastapi import FastAPI
from pydantic import BaseModel
from rag_core import ask

app = FastAPI()

class AskBody(BaseModel):
    query: str
    session_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask_endpoint(body: AskBody):
    return ask(body.query, session_id=body.session_id)
