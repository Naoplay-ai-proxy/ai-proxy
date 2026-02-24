from fastapi import APIRouter, HTTPException, Depends
from .models import MeetingSummaryRequest, MeetingSummaryResponse
from .llm_client import LLMClient, get_llm_client
from .prompts import get_system_prompt

router = APIRouter()

@router.post("/meeting-summary", response_model=MeetingSummaryResponse)
async def process_meeting_summary(
    request: MeetingSummaryRequest, 
    llm: LLMClient = Depends(get_llm_client)
):
    
    try:
        # 1. TRADUCTION DU CODE LANGUE
        target_lang = "French" if request.language == "fr" else "English"

        # 2. GÉNÉRATION DU PROMPT SYSTÈME
        system_instructions = get_system_prompt(language=target_lang)

        # 3. SÉCURISATION DU MESSAGE UTILISATEUR
        # On respecte la consigne de sécurité du prompt (delimiteurs)
        user_content = f"TRANSCRIPT START:\n{request.transcript}\nTRANSCRIPT END"

        # 4. APPEL DU CLIENT LLM
        ai_data = await llm.ask_structured(
            system_instructions=system_instructions,
            user_message=user_content
        )

        # 5. RETOUR VALIDÉ
        # FastAPI vérifiera automatiquement que cet objet respecte MeetingSummaryResponse
        return MeetingSummaryResponse(
            meeting_id=request.meeting_id,
            summary=ai_data["summary"],
            actions=ai_data["actions"]
        )

    except Exception as e:
        # On log l'erreur et on renvoie une 500 propre
        print(f"[TASK 7 ERROR] Integration failure: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to process meeting summary due to an internal error."
        )
