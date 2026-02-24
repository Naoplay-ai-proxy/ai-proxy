import litellm
import os
from typing import Dict, Any

class LLMClient:
    def __init__(self, model_name: str = "openai/gpt-4o"):
        """
        Initialise le client avec un modèle par défaut.
        La Tâche 6 viendra ensuite configurer les clés API réelles.
        """
        self.model_name = model_name
        # LiteLLM utilise les variables d'environnement (OPENAI_API_KEY, etc.)

    async def ask_structured(
        self, 
        system_instructions: str, 
        user_message: str, 
        model_version: str = "v1"
    ) -> Dict[str, Any]:
        """
        Méthode unique d'appel (Abstraction demandée par la Tâche 5).
        """
        try:
            # Appel asynchrone au LLM
            response = await litellm.acompletion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}, # On impose le JSON
                timeout=30 # Gestion simple du timeout
            )

            # Extraction du contenu JSON
            content = response.choices[0].message.content
            
            # Ici, LiteLLM nous renvoie souvent du texte qu'il faut parser
            import json
            return json.loads(content)

        except Exception as e:
            # Gestion d'erreur générique (Tâche 5)
            # On loggue l'erreur réelle mais on lève une exception propre
            print(f"Erreur LLMClient [{model_version}]: {str(e)}")
            raise RuntimeError("Échec de la communication avec le fournisseur LLM")

# Fonction d'usine (Factory) pour l'injection de dépendances (utile pour la Tâche 7)
def get_llm_client() -> LLMClient:
    # On pourrait ici lire une config pour savoir quel modèle utiliser
    return LLMClient(model_name=os.getenv("LLM_MODEL", "gpt-4o"))