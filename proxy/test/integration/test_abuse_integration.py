import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from typing import Dict, Any

# Imports de l'application
from proxy.app.schemas.meeting_summary import MeetingSummaryRequest
from proxy.app.main import app
from proxy.app.llm_client import get_llm_client
from proxy.app.prompt import get_system_prompt


class SpyLLMClient:
    def __init__(self):
        self.last_user_message = None
        self.last_system_prompt = None

    async def ask_structured(self, system_instructions: str, user_message: str) -> Dict[str, Any]:
        self.last_user_message = user_message
        self.last_system_prompt = system_instructions
        return {"summary": "Safe", "actions": []}

@pytest.fixture
def spy_client():
    spy = SpyLLMClient()
    app.dependency_overrides[get_llm_client] = lambda: spy
    yield spy
    app.dependency_overrides = {}

client = TestClient(app)



@pytest.mark.integration
def test_router_sandboxing(spy_client):
    """
    Si un texte malveillant passe le filtre regex (car pas dans la liste noire),
    le Routeur doit quand même l'enfermer dans les balises TRANSCRIPT.
    """
    # Ce texte n'est pas dans la liste noire du schéma, donc il passe la validation
    clever_attack = "Ceci est une attaque subtile qui ne contient pas les mots clés interdits."
    
    payload = {
        "meeting_id": "TEST-SANDBOX",
        "transcript": clever_attack,
        "language": "fr"
    }

    resp = client.post("/api/v1/meeting-summary", json=payload)
    assert resp.status_code == 200

    # Vérification que le Router a bien fait son travail de "Sandboxing"
    sent_msg = spy_client.last_user_message
    
    assert "TRANSCRIPT START" in sent_msg
    assert clever_attack in sent_msg
    assert "TRANSCRIPT END" in sent_msg
    
    # Vérification de l'ordre : L'attaque est BIEN après le début du bloc
    assert sent_msg.find("TRANSCRIPT START") < sent_msg.find(clever_attack)
