import json
import logging
from typing import Any, Dict

import litellm
import openai

from .errors import (
    UnexpectedTechnicalError,
    UpstreamRateLimitError,
    UpstreamServiceError,
    UpstreamTimeoutError,
)


logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, *, api_key: str, model_name: str):
        # Valeurs injectées depuis les settings chargés au startup
        self.model_name = model_name
        self.api_key = api_key

    async def ask_structured(self, system_instructions: str, user_message: str) -> Dict[str, Any]:
        """
        Appelle le provider via LiteLLM et attend une réponse JSON structurée.
        """
        try:
            response = await litellm.acompletion(
                model=self.model_name,
                api_key=self.api_key,
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_message},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                # Timeout explicite pour mieux distinguer le cas timeout provider
                timeout=30,
                # Pas de retry automatique pour garder un comportement prévisible
                num_retries=0,
            )

            # Contenu JSON renvoyé par le modèle
            raw_content = response.choices[0].message.content
            data = json.loads(raw_content)

            # Normalisation défensive des actions
            cleaned_actions = [
                {
                    "owner": action.get("owner", "Unassigned"),
                    "description": action.get("description", action.get("task", "No description")),
                }
                for action in data.get("actions", [])
            ]

            return {
                "summary": data.get("summary", "No summary provided"),
                "actions": cleaned_actions,
            }

        except openai.APITimeoutError:
            # Timeout provider : log côté serveur uniquement
            logger.warning(
                "llm_timeout",
                extra={"event": "llm_timeout"},
            )
            raise UpstreamTimeoutError()

        except openai.RateLimitError:
            # 429 provider : transformé en indisponibilité temporaire côté client
            logger.warning(
                "llm_rate_limit",
                extra={"event": "llm_rate_limit"},
            )
            raise UpstreamRateLimitError()

        except (openai.APIError, openai.InternalServerError):
            # 5xx provider : transformé en erreur de service upstream
            logger.error(
                "llm_upstream_service_error",
                extra={"event": "llm_upstream_service_error"},
            )
            raise UpstreamServiceError()

        except Exception:
            # Toute autre erreur technique devient une erreur générique contrôlée
            logger.exception(
                "llm_unexpected_error",
                extra={"event": "llm_unexpected_error"},
            )
            raise UnexpectedTechnicalError()


class MockLLMClient:
    async def ask_structured(self, system_instructions: str, user_message: str) -> Dict[str, Any]:
        # Réponse stable pour tests locaux / end-to-end sans provider réel
        return {
            "summary": "MOCK: résumé de test (pas de vrai LLM).",
            "actions": [
                {"owner": "Unknown", "description": "MOCK: action de test"}
            ]
        }


def build_llm_client(settings):
    # Mode mock activé explicitement
    if settings.llm_mode.lower() in ("mock", "1", "true", "yes"):
        return MockLLMClient()

    # Fallback historique si le nom de modèle vaut mock
    if settings.llm_model_name.lower() == "mock":
        return MockLLMClient()

    # Client réel construit à partir des settings centralisés
    return LLMClient(
        api_key=settings.llm_api_key,
        model_name=settings.llm_model_name,
    )