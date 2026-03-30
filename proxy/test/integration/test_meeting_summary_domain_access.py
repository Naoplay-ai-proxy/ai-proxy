from types import SimpleNamespace

from fastapi.testclient import TestClient

from proxy.app.core.auth import AuthenticatedUser
from proxy.app.dependencies.security import require_authenticated_user
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


def test_meeting_summary_rejects_user_outside_workspace_domain_without_calling_llm() -> None:
    dummy_llm = DummyLLMClient()
    app.state.llm_client = dummy_llm
    app.state.settings = build_settings()

    def override_require_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(
            sub="external-user-1",
            email="user@external-company.com",
            hd="external-company.com",
        )

    app.dependency_overrides[require_authenticated_user] = override_require_authenticated_user

    client = TestClient(app)

    response = client.post(
        "/meeting-summary",
        json={
            "meeting_id": "meeting-001",
            "transcript": "Bonjour",
            "language": "fr",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access restricted to Google Workspace domain users"
    assert dummy_llm.called is False

    app.dependency_overrides.clear()