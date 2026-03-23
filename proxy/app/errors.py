"""
errors.py

Erreurs contrôlées du proxy.

But :
- exposer un contrat d'erreur stable au client
- ne jamais renvoyer les messages bruts du provider
- garder la logique de mapping d'erreurs côté serveur
"""


class ProxyError(Exception):
    """
    Classe de base pour toutes les erreurs contrôlées du proxy.
    """

    def __init__(self, message: str, code: str, status_code: int, retryable: bool = False):
        # Message lisible renvoyé au client
        self.message = message

        # Code d'erreur stable pour le client / front / intégration
        self.code = code

        # Code HTTP à renvoyer
        self.status_code = status_code

        # Indique si le client peut raisonnablement réessayer
        self.retryable = retryable

        # Initialise Exception avec le message
        super().__init__(message)


class UpstreamTimeoutError(ProxyError):
    """
    Le provider IA n'a pas répondu dans le délai attendu.
    """

    def __init__(self):
        super().__init__(
            message="Le service IA n'a pas répondu à temps.",
            code="UPSTREAM_TIMEOUT",
            status_code=504,
            retryable=True,
        )


class UpstreamRateLimitError(ProxyError):
    """
    Le provider IA est temporairement saturé ou limite la requête.
    """

    def __init__(self):
        super().__init__(
            message="Le service IA est temporairement indisponible.",
            code="UPSTREAM_TEMPORARILY_UNAVAILABLE",
            status_code=503,
            retryable=True,
        )


class UpstreamServiceError(ProxyError):
    """
    Le provider IA a renvoyé une erreur serveur ou n'est pas joignable.
    """

    def __init__(self):
        super().__init__(
            message="Le service IA est temporairement indisponible.",
            code="UPSTREAM_SERVICE_ERROR",
            status_code=502,
            retryable=True,
        )


class InvalidUpstreamResponseError(ProxyError):
    """
    Le provider IA a répondu, mais avec un contenu inexploitable ou inattendu.
    """

    def __init__(self):
        super().__init__(
            message="Le service IA a renvoyé une réponse invalide.",
            code="INVALID_UPSTREAM_RESPONSE",
            status_code=502,
            retryable=True,
        )


class ServiceMisconfigurationError(ProxyError):
    """
    Le proxy est mal configuré pour appeler le provider IA.
    """

    def __init__(self):
        super().__init__(
            message="Le service IA est momentanément indisponible.",
            code="SERVICE_MISCONFIGURATION",
            status_code=500,
            retryable=False,
        )


class UnexpectedTechnicalError(ProxyError):
    """
    Erreur technique inattendue dans le proxy.
    """

    def __init__(self):
        super().__init__(
            message="Une erreur technique est survenue.",
            code="INTERNAL_TECHNICAL_ERROR",
            status_code=500,
            retryable=False,
        )
