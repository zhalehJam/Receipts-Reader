from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="My Project API",
    version="0.1.0",
    description="API to call project functions",
)

class AddRequest(BaseModel):
    a: int
    b: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/add")
def add(req: AddRequest):
    return {"result": req.a + req.b}

@app.get("/config-example")
def config_example():
    # Example: read from .env
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API_KEY is missing in .env")
    return {"api_key_loaded": True}
