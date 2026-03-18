from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.agent.graph import sql_agent

app = FastAPI(title="SQL AI Agent")

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(req: QuestionRequest):
    try:
        result = sql_agent.invoke({"question": req.question})
        return {
            "question": req.question,
            "sql":      result.get("sql_current", ""),
            "feedback": result.get("feedback", ""),
            "answer":   result.get("final_answer", ""),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "hint": "Check your OpenRouter API key and model name in .env"}
        )

@app.get("/health")
def health():
    return {"status": "ok"}