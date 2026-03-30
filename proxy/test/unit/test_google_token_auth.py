from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from proxy.app.dependencies.security import require_authenticated_user


def build_request(client_id: str = "test-client-id") -> SimpleNamespace:
    settings = SimpleNamespace(google_web_client_id=client_id)
    app = SimpleNamespace(state=SimpleNamespace(settings=settings))
    return SimpleNamespace(app=app)


def test_require_authenticated_user_rejects_missing_bearer_token() -> None:
    request = build_request()

    with pytest.raises(HTTPException) as exc_info:
        require_authenticated_user(request=request, authorization=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing bearer token"


@patch("proxy.app.dependencies.security.id_token.verify_oauth2_token")
def test_require_authenticated_user_rejects_invalid_token(mock_verify) -> None:
    request = build_request()
    mock_verify.side_effect = ValueError("invalid token")

    with pytest.raises(HTTPException) as exc_info:
        require_authenticated_user(
            request=request,
            authorization="Bearer fake-token",
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


@patch("proxy.app.dependencies.security.id_token.verify_oauth2_token")
def test_require_authenticated_user_rejects_expired_token(mock_verify) -> None:
    request = build_request()
    mock_verify.side_effect = ValueError("token expired")

    with pytest.raises(HTTPException) as exc_info:
        require_authenticated_user(
            request=request,
            authorization="Bearer expired-token",
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


@patch("proxy.app.dependencies.security.id_token.verify_oauth2_token")
def test_require_authenticated_user_rejects_token_without_sub(mock_verify) -> None:
    request = build_request()
    mock_verify.return_value = {
        "email": "user@naoplay.fr",
        "hd": "naoplay.fr",
    }

    with pytest.raises(HTTPException) as exc_info:
        require_authenticated_user(
            request=request,
            authorization="Bearer valid-token",
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


@patch("proxy.app.dependencies.security.id_token.verify_oauth2_token")
def test_require_authenticated_user_rejects_token_without_email(mock_verify) -> None:
    request = build_request()
    mock_verify.return_value = {
        "sub": "123456",
        "hd": "naoplay.fr",
    }

    with pytest.raises(HTTPException) as exc_info:
        require_authenticated_user(
            request=request,
            authorization="Bearer valid-token",
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


@patch("proxy.app.dependencies.security.id_token.verify_oauth2_token")
def test_require_authenticated_user_returns_authenticated_user(mock_verify) -> None:
    request = build_request()
    mock_verify.return_value = {
        "sub": "123456",
        "email": "user@naoplay.fr",
        "hd": "naoplay.fr",
    }

    user = require_authenticated_user(
        request=request,
        authorization="Bearer valid-token",
    )

    assert user.sub == "123456"
    assert user.email == "user@naoplay.fr"
    assert user.hd == "naoplay.fr"