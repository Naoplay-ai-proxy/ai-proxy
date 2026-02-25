from fastapi import APIRouter, HTTPException, Depends
from .schemas.meeting_summary import MeetingSummaryRequest, MeetingSummaryResponse
from .llm_client import LLMClient, get_llm_client
from .prompt import get_system_prompt 

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
        user_content = f"TRANSCRIPT START:\n{request.transcript}\nTRANSCRIPT END"

        # 4. APPEL DU CLIENT LLM
        ai_data = await llm.ask_structured(
            system_instructions=system_instructions,
            user_message=user_content
        )

        # 5. RETOUR VALIDÉ
        return MeetingSummaryResponse(
            meeting_id=request.meeting_id,
            summary=ai_data["summary"],
            actions=ai_data["actions"]
        )

    except Exception as e:
        print(f"[ERROR] Integration failure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
