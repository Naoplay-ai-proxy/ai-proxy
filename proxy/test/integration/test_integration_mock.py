import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
from proxy.app.main import app
from proxy.app.llm_client import get_llm_client


class FakeLLMClient:

    async def ask_structured(self, system_instructions: str, user_message: str) -> Dict[str, Any]:
        return {
            "summary": "Ceci est un résumé simulé par le test.",
            "actions": [
                {"owner": "Alice", "description": "Envoyer le rapport"},
                {"owner": "Bob", "description": "Valider le budget"}
            ]
        }

@pytest.fixture
def client_mocked():

    app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient()
    
    with TestClient(app) as c:
        yield c  # On donne le client au test
    
	# pour ne pas polluer les autres tests
    app.dependency_overrides = {}


@pytest.mark.integration
def test_api_meeting_summary_mocked(client_mocked):

    payload = {
        "meeting_id": "test-mock-01",
        "language": "fr",
        "transcript": "Peu importe le texte ici, le FakeLLMClient renvoie toujours la même chose."
    }

    response = client_mocked.post("/api/v1/meeting-summary", json=payload)

    assert response.status_code == 200, f"Erreur: {response.text}"
    data = response.json()

    # assert data["meeting_id"] == "test-mock-01"
    # assert data["summary"] == "Ceci est un résumé simulé par le test."
    # assert len(data["actions"]) == 2

@pytest.mark.integration
def test_api_validation_still_works(client_mocked):
    payload = {
        "meeting_id": "fail",
        "transcript": "", # Vide -> Doit échouer
        "language": "fr"
    }
    response = client_mocked.post("/api/v1/meeting-summary", json=payload)
    assert response.status_code == 422
