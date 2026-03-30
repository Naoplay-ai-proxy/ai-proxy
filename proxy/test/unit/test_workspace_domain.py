import pytest
from fastapi import HTTPException

from proxy.app.core.auth import AuthenticatedUser, ensure_allowed_workspace_domain


def test_workspace_domain_allows_naoplay_user() -> None:
    user = AuthenticatedUser(
        sub="123",
        email="alice@naoplay.fr",
        hd="naoplay.fr",
    )

    ensure_allowed_workspace_domain(user, "naoplay.fr")


def test_workspace_domain_rejects_gmail_user() -> None:
    user = AuthenticatedUser(
        sub="123",
        email="alice@gmail.com",
        hd=None,
    )

    with pytest.raises(HTTPException) as exc_info:
        ensure_allowed_workspace_domain(user, "naoplay.fr")

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access restricted to Google Workspace domain users"


def test_workspace_domain_rejects_other_workspace_domain() -> None:
    user = AuthenticatedUser(
        sub="123",
        email="alice@othercompany.com",
        hd="othercompany.com",
    )

    with pytest.raises(HTTPException) as exc_info:
        ensure_allowed_workspace_domain(user, "naoplay.fr")

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access restricted to Google Workspace domain users"


def test_workspace_domain_rejects_if_hd_missing_even_with_naoplay_email() -> None:
    user = AuthenticatedUser(
        sub="123",
        email="alice@naoplay.fr",
        hd=None,
    )

    with pytest.raises(HTTPException) as exc_info:
        ensure_allowed_workspace_domain(user, "naoplay.fr")

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access restricted to Google Workspace domain users"