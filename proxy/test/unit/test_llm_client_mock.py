import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from proxy.app.llm_client import LLMClient

# Simule la structure JSON spécifique retournée par OpenAI/Anthropic 
# pour tester la logique de parsing sans appel réseau.
MOCK_LITELLM_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": '{"summary": "Test Summary", "actions": [{"owner": "Bob", "task": "Do work"}]}'
            }
        }
    ]
}

@pytest.mark.unit
@pytest.mark.asyncio
async def test_ask_structured_parsing():
    # Valide la capacité du client à extraire et nettoyer la réponse en mode 'json_object',
    # indépendamment du fournisseur LLM sous-jacent.
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"summary": "Bravo", "actions": [{"owner": "Alice", "description": "Test"}]}'
    

    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
		# Injection d'une fausse clé API pour contourner la vérification à l'initialisation du client.
        with patch.dict("os.environ", {"LLM_API_KEY": "fake-key"}):
            client = LLMClient()
            result = await client.ask_structured("sys", "user")


    assert result["summary"] == "Bravo"
    assert len(result["actions"]) == 1
    assert result["actions"][0]["owner"] == "Alice"
