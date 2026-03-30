from fastapi import Depends, Header, HTTPException, Request, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from proxy.app.core.auth import AuthenticatedUser, ensure_allowed_workspace_domain


def require_authenticated_user(
    request: Request,
    authorization: str | None = Header(default=None),
) -> AuthenticatedUser:
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    
    token = authorization.removeprefix("Bearer ").strip()
    settings = request.app.state.settings

    if not settings.google_web_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Missing Google web client configuration",
        )
    try:
        # La vérification côté serveur empêche de faire confiance à un jeton
        # simplement décodé côté client ou copié depuis l'interface du navigateur.
        claims = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.google_web_client_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc
    sub = claims.get("sub")
    email = claims.get("email")
    hd = claims.get("hd")
    if not sub or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )
    return AuthenticatedUser(
        sub=sub, 
        email=email, 
        hd=hd
                             
                             )



def require_naoplay_user(
    request: Request,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> AuthenticatedUser:
    allowed_domain = request.app.state.settings.allowed_google_domain
    ensure_allowed_workspace_domain(user, allowed_domain)
    return user