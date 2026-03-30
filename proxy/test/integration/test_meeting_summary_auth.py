from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from proxy.app.main import app


class DummyLLMClient:
    def __init__(self) -> None:
        self.called = False

    async def ask_structured(self, system_instructions, user_message):
        self.called = True
        return {
            "summary": "Résumé",
            "actions": [],
        }

def build_settings() -> SimpleNamespace:
    return SimpleNamespace(
        google_web_client_id="test-client-id",
        allowed_google_domain="naoplay.fr",
    )

def test_meeting_summary_rejects_missing_token_without_calling_llm() -> None:
    dummy_llm = DummyLLMClient()
    app.state.llm_client = dummy_llm
    app.state.settings = build_settings()
    client = TestClient(app)

    response = client.post(
        "/meeting-summary",
        json={
            "meeting_id": "meeting-001",
            "transcript": "Bonjour",
            "language": "fr",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"
    assert dummy_llm.called is False


@patch("proxy.app.dependencies.security.id_token.verify_oauth2_token")
def test_meeting_summary_rejects_invalid_token_without_calling_llm(mock_verify) -> None:
    mock_verify.side_effect = ValueError("invalid token")

    dummy_llm = DummyLLMClient()
    app.state.llm_client = dummy_llm

    client = TestClient(app)

    response = client.post(
        "/meeting-summary",
        headers={"Authorization": "Bearer fake-token"},
        json={
            "meeting_id": "meeting-001",
            "transcript": "Bonjour",
            "language": "fr",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
    assert dummy_llm.called is False