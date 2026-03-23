import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .core.settings import load_settings
from .errors import ProxyError
from .llm_client import build_llm_client
from .router import router as api_router


load_dotenv()

# Logging de base pour l'application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Proxy for Google Chat",
    description="Backend gouverné pour traitement IA",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event() -> None:
    # Charge la configuration applicative
    settings = load_settings()

    # Rend les settings accessibles dans l'app
    app.state.settings = settings

    # Construit le client LLM une seule fois au démarrage
    app.state.llm_client = build_llm_client(settings)


# La version de l'API est gérée par Gravitee dans l'uri, pas besoin de préfixe ici
app.include_router(api_router)


@app.exception_handler(ProxyError)
async def proxy_error_handler(request: Request, exc: ProxyError):
    """
    Handler global des erreurs contrôlées du proxy.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Handler de secours pour éviter toute fuite d'information interne.
    """
    # Détail complet dans les logs serveur uniquement
    logger.exception("unhandled_exception")

    # Réponse générique côté client
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_TECHNICAL_ERROR",
                "message": "Une erreur technique est survenue.",
                "retryable": False,
            }
        },
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-proxy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)