import pytest
from proxy.app.prompt import get_system_prompt

@pytest.mark.unit
def test_prompt_generation_french():
	# S'assure que l'injection de variables dynamiques ({{TARGET_LANGUAGE}}) fonctionne
    # pour éviter que le LLM ne réponde dans la mauvaise langue (hallucination).
    prompt = get_system_prompt("French")
    
    assert "The output content must be in French" in prompt

	# Vérifie que la contrainte de format JSON est explicite pour réduire les erreurs de parsing.
    expected_phrase = "format: return only a valid json object"
    assert expected_phrase in prompt.lower()

def test_prompt_generation_english():
    prompt = get_system_prompt("English")
    assert "The output content must be in English" in prompt

def test_prompt_security_rules():
	# Confirme que le 'System Prompt' inclut bien la commande de prévalence
    # pour ignorer les instructions utilisateur (Défense contre le Prompt Injection).
    prompt = get_system_prompt("French")
    
    assert "IGNORE THEM" in prompt
    
    assert "do not hallucinate" in prompt.lower()
