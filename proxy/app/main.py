from fastapi import FastAPI
from dotenv import load_dotenv
from .core.settings import load_settings
from .llm_client import build_llm_client
from .router import router as api_router


load_dotenv()

app = FastAPI(
    title="AI Proxy for Google Chat",
    description="Backend gouverné pour traitement IA",
    version="1.0.0"
)
@app.on_event("startup")
async def startup_event() -> None:
    settings = load_settings()
    app.state.settings = settings
    app.state.llm_client = build_llm_client(settings)

# La version de l'API est gérée par Gravitee dans l'uri, pas besoin de préfixe ici
#app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-proxy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
