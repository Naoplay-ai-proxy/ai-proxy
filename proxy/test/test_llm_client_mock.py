import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from proxy.app.llm_client import LLMClient

# Donnée simulée (ce que LiteLLM renverrait normalement)
MOCK_LITELLM_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": '{"summary": "Test Summary", "actions": [{"owner": "Bob", "task": "Do work"}]}'
            }
        }
    ]
}

@pytest.mark.asyncio
async def test_ask_structured_parsing():
    """
    Teste que le client parse correctement la réponse JSON brute du LLM.
    On 'patch' litellm.acompletion pour qu'il ne fasse pas d'appel réseau.
    """
    # 1. On configure le Mock
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"summary": "Bravo", "actions": [{"owner": "Alice", "description": "Test"}]}'
    
    # 2. On applique le patch sur la fonction acompletion
    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        # 3. On instancie le client (avec une fausse clé pour passer le __init__)
        with patch.dict("os.environ", {"LLM_API_KEY": "fake-key"}):
            client = LLMClient()
            result = await client.ask_structured("sys", "user")

    # 4. Vérifications
    assert result["summary"] == "Bravo"
    assert len(result["actions"]) == 1
    assert result["actions"][0]["owner"] == "Alice"
