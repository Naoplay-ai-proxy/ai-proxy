from __future__ import annotations

import os
from dataclasses import dataclass

from .secrets import SecretManagerProvider, SecretRef


def _parse_allowed_languages(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]


@dataclass
class AppSettings:
    llm_api_key: str
    llm_model_name: str
    llm_mode: str
    max_transcript_length: int
    allowed_languages: list[str]
    gcp_project_id: str | None
    llm_api_key_secret_id: str
    llm_api_key_secret_version: str
    allowed_google_domain : str= "naoplay.fr"
    google_web_client_id: str = ""


def load_settings() -> AppSettings:
    """
    En prod: charge LLM_API_KEY depuis Google Secret Manager
    En local: fallback possible sur LLM_API_KEY si présent dans l'environnement
    """
    llm_api_key = os.getenv("LLM_API_KEY")
    gcp_project_id = os.getenv("GCP_PROJECT_ID")
    llm_api_key_secret_id = os.getenv("LLM_API_KEY_SECRET_ID", "LLM_API_KEY")
    llm_api_key_secret_version = os.getenv("LLM_API_KEY_SECRET_VERSION", "latest")
    allowed_google_domain = os.getenv("ALLOWED_GOOGLE_DOMAIN", "naoplay.fr")
    google_web_client_id = os.getenv("GOOGLE_WEB_CLIENT_ID", "").strip()
    if not llm_api_key:
        if not gcp_project_id:
            raise RuntimeError(
                "Missing GCP_PROJECT_ID. Required when LLM_API_KEY is not provided."
            )

        provider = SecretManagerProvider()
        llm_api_key = provider.get_secret(
            SecretRef(
                project_id=gcp_project_id,
                secret_id=llm_api_key_secret_id,
                version=llm_api_key_secret_version,
            )
        )

    llm_model_name = os.getenv("LLM_MODEL_NAME", "gpt-4.1-mini")
    llm_mode = os.getenv("LLM_MODE", llm_model_name)
    max_transcript_length = int(os.getenv("MAX_TRANSCRIPT_LENGTH", "50000"))
    allowed_languages = _parse_allowed_languages(
        os.getenv("ALLOWED_LANGUAGES", "fr,en")
    )

    return AppSettings(
        llm_api_key=llm_api_key,
        llm_model_name=llm_model_name,
        llm_mode=llm_mode,
        max_transcript_length=max_transcript_length,
        allowed_languages=allowed_languages,
        gcp_project_id=gcp_project_id,
        llm_api_key_secret_id=llm_api_key_secret_id,
        llm_api_key_secret_version=llm_api_key_secret_version,
        allowed_google_domain=allowed_google_domain,
        google_web_client_id=google_web_client_id,
    )