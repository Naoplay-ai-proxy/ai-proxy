from dataclasses import dataclass
from fastapi import HTTPException, status


@dataclass
class AuthenticatedUser:
    sub: str
    email: str
    hd: str | None = None



def ensure_allowed_workspace_domain(
    user: AuthenticatedUser,
    allowed_domain: str,
) -> None:
    normalized_domain = allowed_domain.strip().lower()
    normalized_email = user.email.strip().lower()
    normalized_hd = user.hd.strip().lower() if user.hd else None

    email_allowed = normalized_email.endswith(f"@{normalized_domain}")
    hd_allowed = normalized_hd == normalized_domain

    if not email_allowed or not hd_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Google Workspace domain users",
        )