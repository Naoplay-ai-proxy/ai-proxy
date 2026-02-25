import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
from proxy.app.main import app
from proxy.app.llm_client import get_llm_client, LLMClient

# --- 1. Définition du Mock ---
class FakeLLMClient:
    """Un client qui ne réfléchit pas et renvoie toujours une réponse fixe."""
    async def ask_structured(self, system_instructions: str, user_message: str) -> Dict[str, Any]:
        # On simule une réponse parfaite
        return {
            "summary": "Ceci est un résumé simulé par le test.",
            "actions": [
                {"owner": "Alice", "description": "Envoyer le rapport"},
                {"owner": "Bob", "description": "Valider le budget"}
            ]
        }

# --- 2. Configuration du test ---
# On remplace la dépendance réelle par notre FakeLLMClient
app.dependency_overrides[get_llm_client] = lambda: FakeLLMClient()

client = TestClient(app)

def test_api_meeting_summary_mocked():
    """
    Test d'intégration E2E SANS CLÉ API.
    Le routeur fonctionne, la validation fonctionne, mais le LLM est simulé.
    """
    payload = {
        "meeting_id": "test-mock-01",
        "language": "fr",
        "transcript": "Peu importe le texte ici, le FakeLLMClient renvoie toujours la même chose."
    }

    # Appel
    response = client.post("/api/v1/meeting-summary", json=payload)

    # Vérifications HTTP
    assert response.status_code == 200, f"Erreur: {response.text}"
    data = response.json()

    # Vérifications Contenu (Basé sur ce que FakeLLMClient renvoie)
    print("\n✅ RÉPONSE (MOCK) :", data)
    assert data["meeting_id"] == "test-mock-01"
    assert data["summary"] == "Ceci est un résumé simulé par le test."
    assert len(data["actions"]) == 2
    assert data["actions"][0]["owner"] == "Alice"

def test_api_validation_still_works():
    """Vérifie que même mocké, la validation des entrées (Pydantic) reste active"""
    payload = {
        "meeting_id": "fail",
        "transcript": "", # Vide -> Doit échouer
        "language": "fr"
    }
    response = client.post("/api/v1/meeting-summary", json=payload)
    assert response.status_code == 422
