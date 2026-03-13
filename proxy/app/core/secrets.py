from __future__ import annotations

import logging
from dataclasses import dataclass
from threading import Lock

import google_crc32c
from google.cloud import secretmanager


logger = logging.getLogger(__name__)


class SecretAccessError(RuntimeError):
    """Erreur d'accès à Google Secret Manager."""


@dataclass(frozen=True)
class SecretRef:
    project_id: str
    secret_id: str
    version: str = "latest"

    @property
    def resource_name(self) -> str:
        return (
            f"projects/{self.project_id}/secrets/"
            f"{self.secret_id}/versions/{self.version}"
        )


class SecretManagerProvider:
    """
    Lire un secret depuis Google Secret Manager avec cache mémoire 
    Authentification via ADC (service account attaché à la VM)
    """

    def __init__(self) -> None:
        self._client = secretmanager.SecretManagerServiceClient()
        self._cache: dict[str, str] = {}
        self._lock = Lock()

    def get_secret(self, ref: SecretRef, *, timeout: float = 5.0) -> str:
        cache_key = ref.resource_name

        if cache_key in self._cache:
            return self._cache[cache_key]

        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

            try:
                response = self._client.access_secret_version(
                    request={"name": ref.resource_name},
                    timeout=timeout,
                )
            except Exception as exc:
                logger.exception(
                    "Impossible de lire le secret depuis Secret Manager",
                    extra={
                        "project_id": ref.project_id,
                        "secret_id": ref.secret_id,
                        "version": ref.version,
                    },
                )
                raise SecretAccessError(
                    f"Unable to access secret '{ref.secret_id}'"
                ) from exc

            payload = response.payload.data

            crc32c = google_crc32c.Checksum()
            crc32c.update(payload)
            checksum_int = int(crc32c.hexdigest(), 16)

            if response.payload.data_crc32c != checksum_int:
                raise SecretAccessError(
                    f"Checksum verification failed for secret '{ref.secret_id}'"
                )

            try:
                secret_value = payload.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise SecretAccessError(
                    f"Secret '{ref.secret_id}' is not valid UTF-8"
                ) from exc

            self._cache[cache_key] = secret_value
            logger.info(
                "Secret loaded successfully from Secret Manager",
                extra={
                    "project_id": ref.project_id,
                    "secret_id": ref.secret_id,
                    "version": ref.version,
                },
            )
            return secret_value