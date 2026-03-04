import pytest
from fastapi.testclient import TestClient
from proxy.app.main import app  # On importe l'application FastAPI réelle

# Création du client de test (simule le navigateur/curl)
client = TestClient(app)

@pytest.mark.ai_call
def test_api_meeting_summary_nominal():

    payload = {
        "meeting_id": "test-integration-001",
        "language": "fr",
        "transcript": """
        Alice: Bonjour Bob, est-ce que le rapport financier est prêt ?
        Bob: Pas encore Alice, j'ai besoin des chiffres de la comptabilité.
        Alice: D'accord, je vais demander à Charlie de te les envoyer avant midi.
        Bob: Merci, c'est parfait.
        """
    }


    print("\n--- Appel de l'API simulé ---")
    response = client.post("/api/v1/meeting-summary", json=payload)

    assert response.status_code == 200, f"Erreur API: {response.text}"


    data = response.json()
    

    print("\n✅ RÉPONSE REÇUE :")
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False))


    assert data["meeting_id"] == "test-integration-001"
    assert "summary" in data
    assert len(data["summary"]) > 0
    assert "actions" in data
    assert len(data["actions"]) > 0
    
    # Vérification fine : On s'attend à ce que l'IA ait trouvé l'action d'Alice
    # Note : Ce test dépend de la qualité du LLM, il peut être fragile si le modèle change
    action_descriptions = [a["description"].lower() for a in data["actions"]]
    assert any("chiffres" in d or "comptabilité" in d for d in action_descriptions), \
        "L'action concernant les chiffres de comptabilité n'a pas été trouvée"

@pytest.mark.integration
def test_api_validation_error():
    payload = {
        "meeting_id": "test-fail",
        "transcript": "", # Vide -> Interdit
        "language": "fr"
    }
    
    response = client.post("/api/v1/meeting-summary", json=payload)
    
    # On s'attend à une erreur 422 (Unprocessable Entity - Erreur de validation FastAPI)
    assert response.status_code == 422
    print("\n✅ Erreur de validation correctement détectée (422)")
