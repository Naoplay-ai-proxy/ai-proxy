import litellm
import os
import json
from typing import Dict, Any
from .schemas.meeting_summary import MeetingSummaryResponse # Import de la Tâche 2 pour référence

class LLMClient:
    def __init__(self):
        # Configuration du provider via variables d'environnement
        # Exemple: "openai/gpt-4o" ou "anthropic/claude-3-5-sonnet-20240620"
        self.model_name = os.getenv("LLM_MODEL_NAME", "openai/gpt-4o")
        self.api_key = os.getenv("LLM_API_KEY")
        
        # Sécurité : Vérifier que la clé est présente au démarrage
        if not self.api_key:
            raise ValueError("LLM_API_KEY is missing in environment variables")

    async def ask_structured(
        self, 
        system_instructions: str, 
        user_message: str
    ) -> Dict[str, Any]:
        """
        Tâche 6 : Appel API Réel & Parsing robuste
        """
        try:
            # Appel réel via LiteLLM
            # Il gère automatiquement les headers Auth selon le préfixe du modèle
            response = await litellm.acompletion(
                model=self.model_name,
                api_key=self.api_key,
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.2, # Basse pour plus de stabilité/fidélité
                max_tokens=2000
            )

            # 1. Extraction du contenu textuel
            raw_content = response.choices[0].message.content

            # 2. Parsing JSON (Transformation String -> Dict)
            data = json.loads(raw_content)

            # 3. Nettoyage strict (Pour respecter Pydantic Tâche 2)
            # On ne garde QUE ce qui est dans MeetingSummaryResponse
            cleaned_actions = [
                {
                    "owner": action.get("owner", "Unassigned"),
                    "description": action.get("description", action.get("task", "No description"))
                }
                for action in data.get("actions", [])
            ]

            return {
                "summary": data.get("summary", "No summary provided"),
                "actions": cleaned_actions
            }

        except Exception as e:
            # Log détaillé pour la Tâche 5 (Observabilité)
            print(f"[LLM_ERROR] Failed call to {self.model_name}: {str(e)}")
            raise RuntimeError(f"LLM Provider Error: {str(e)}")
    def get_llm_client() :
        return LLMClient()
