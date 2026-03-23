import json
import logging
from typing import Any, Dict, List

import litellm
import openai

from .errors import (
    InvalidUpstreamResponseError,
    ServiceMisconfigurationError,
    UnexpectedTechnicalError,
    UpstreamRateLimitError,
    UpstreamServiceError,
    UpstreamTimeoutError,
    ProxyError,
)


logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, *, api_key: str, model_name: str):
        # Valeurs injectées depuis les settings chargés au startup
        self.model_name = model_name
        self.api_key = api_key

    @staticmethod
    def _normalize_actions(actions: Any) -> List[Dict[str, str]]:
        """
        Vérifie et normalise la liste d'actions renvoyée par le provider.
        """
        if actions is None:
            return []

        if not isinstance(actions, list):
            raise  ()

        cleaned_actions: List[Dict[str, str]] = []
        for action in actions:
            if not isinstance(action, dict):
                raise InvalidUpstreamResponseError()

            owner = action.get("owner", "Unassigned")
            description = action.get("description", action.get("task", "No description"))

            if owner is None:
                owner = "Unassigned"
            if description is None:
                description = "No description"

            cleaned_actions.append(
                {
                    "owner": str(owner),
                    "description": str(description),
                }
            )

        return cleaned_actions

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

            try:
                raw_content = response.choices[0].message.content
                #raw_content = "hello" <- test 502.1
            except (AttributeError, IndexError, TypeError):
                logger.error(
                    "llm_invalid_response_shape",
                    extra={"event": "llm_invalid_response_shape"},
                )
                raise InvalidUpstreamResponseError()

            if not raw_content or not isinstance(raw_content, str):
                logger.error(
                    "llm_empty_response_content",
                    extra={"event": "llm_empty_response_content"},
                )
                raise InvalidUpstreamResponseError()

            try:
                data = json.loads(raw_content)
            except json.JSONDecodeError:
                logger.error(
                    "llm_invalid_json_response",
                    extra={"event": "llm_invalid_json_response"},
                )
                raise InvalidUpstreamResponseError()

            if not isinstance(data, dict):
                logger.error(
                    "llm_response_not_object",
                    extra={"event": "llm_response_not_object"},
                )
                raise InvalidUpstreamResponseError()

            summary = data.get("summary", "No summary provided")
            if summary is None:
                summary = "No summary provided"

            cleaned_actions = self._normalize_actions(data.get("actions", []))
            #raise UpstreamRateLimitError() <- test 503
            #raise UpstreamServiceError() <- test 502.2
            return {
                "summary": str(summary),
                "actions": cleaned_actions,
            }

        except InvalidUpstreamResponseError:
            raise

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

        except openai.APIConnectionError:
            # Provider non joignable / souci réseau amont
            logger.error(
                "llm_api_connection_error",
                extra={"event": "llm_api_connection_error"},
            )
            raise UpstreamServiceError()

        except (openai.AuthenticationError, openai.PermissionDeniedError, openai.NotFoundError):
            # Clé API, permissions ou modèle/config invalides côté serveur
            logger.error(
                "llm_provider_misconfiguration",
                extra={"event": "llm_provider_misconfiguration"},
            )
            raise ServiceMisconfigurationError()

        except (openai.APIError, openai.InternalServerError):
            # 5xx provider : transformé en erreur de service upstream
            logger.error(
                "llm_upstream_service_error",
                extra={"event": "llm_upstream_service_error"},
            )
            raise UpstreamServiceError()

        except ProxyError:
            raise

        except Exception:
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
