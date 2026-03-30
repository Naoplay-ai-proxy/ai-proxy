from fastapi import Depends, Header, HTTPException, Request, status

from proxy.app.core.auth import AuthenticatedUser, ensure_allowed_workspace_domain


def require_authenticated_user(
    authorization: str | None = Header(default=None),
) -> AuthenticatedUser:
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    
    token = authorization[len("Bearer ") :].strip()

    if token == "dev-naoplay-user":
        return AuthenticatedUser(
            sub="dev-user-1",
            email="marwa@naoplay.fr",
            hd="naoplay.fr",
            )

    if token == "dev-external-user":
        return AuthenticatedUser(
            sub="dev-user-2",
            email="user@gmail.com",
            hd=None,
            )

    # Ce comportement strict évite d'habituer le service à accepter
    # des identités non vérifiées avant le raccord avec la vraie validation Google.
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        )


def require_naoplay_user(
    request: Request,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> AuthenticatedUser:
    allowed_domain = request.app.state.settings.allowed_google_domain
    ensure_allowed_workspace_domain(user, allowed_domain)
    return user