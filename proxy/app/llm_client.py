import litellm
import os
import json
from typing import Dict, Any
from .schemas.meeting_summary import MeetingSummaryResponse

class LLMClient:
    def __init__(self):
        self.model_name = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
        self.api_key = os.getenv("LLM_API_KEY")
        
        if not self.api_key:
            print("WARNING: LLM_API_KEY is missing. Calls will fail unless mocked.")

    async def ask_structured(self, system_instructions: str, user_message: str) -> Dict[str, Any]:
        try:
            response = await litellm.acompletion(
                model=self.model_name,
                api_key=self.api_key,
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )

            raw_content = response.choices[0].message.content
            data = json.loads(raw_content)

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
            print(f"[LLM_ERROR] Failed call to {self.model_name}: {str(e)}")
            raise RuntimeError(f"LLM Provider Error: {str(e)}")

def get_llm_client() -> LLMClient:
    return LLMClient()