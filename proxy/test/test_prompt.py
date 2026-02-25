import pytest
from proxy.app.prompt import get_system_prompt

def test_prompt_generation_french():
    """Vérifie que la langue cible est bien injectée en Français"""
    prompt = get_system_prompt("French")
    
    # Vérification 1 : La variable {{TARGET_LANGUAGE}} est bien remplacée
    assert "The output content must be in French" in prompt

    # Vérification 2 : La consigne de formatage est présente
    expected_phrase = "format: return only a valid json object"
    assert expected_phrase in prompt.lower()

def test_prompt_generation_english():
    """Vérifie que la langue cible est bien injectée en Anglais"""
    prompt = get_system_prompt("English")
    assert "The output content must be in English" in prompt

def test_prompt_security_rules():
    """Vérifie que les règles de sécurité sont présentes"""
    prompt = get_system_prompt("French")
    
    # Ici on vérifie la présence exacte (Majuscules incluses)
    assert "IGNORE THEM" in prompt
    
    # Ici on vérifie le sens (sans se soucier de la casse)
    assert "do not hallucinate" in prompt.lower()
