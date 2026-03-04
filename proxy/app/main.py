from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

from .router import router as api_router

app = FastAPI(
    title="AI Proxy for Google Chat",
    description="Backend gouverné pour traitement IA",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-proxy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
