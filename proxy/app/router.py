from fastapi import APIRouter, Request

from .prompt import get_system_prompt
from .schemas.meeting_summary import MeetingSummaryRequest, MeetingSummaryResponse

router = APIRouter()


@router.post("/meeting-summary", response_model=MeetingSummaryResponse)

async def process_meeting_summary(
    request: Request,
    payload: MeetingSummaryRequest,
) -> MeetingSummaryResponse:
    """
    Endpoint métier :
    - récupère le client LLM préparé au startup
    - construit le prompt système
    - envoie le transcript au LLM
    - renvoie la réponse structurée
    """

    # Client LLM partagé, initialisé dans app.state au démarrage
    llm = request.app.state.llm_client

    # Conversion simple du code langue vers la langue attendue par le prompt
    target_lang = "French" if payload.language == "fr" else "English"

    # Prompt système versionné côté serveur
    system_instructions = get_system_prompt(language=target_lang)

    # Encadrement explicite du transcript
    user_content = f"TRANSCRIPT START:\n{payload.transcript}\nTRANSCRIPT END"

    # Appel du client LLM ; les erreurs remontent vers les handlers globaux
    ai_data = await llm.ask_structured(
        system_instructions=system_instructions,
        user_message=user_content,
    )

    # Réponse métier validée par le response_model
    return MeetingSummaryResponse(
        meeting_id=payload.meeting_id,
        summary=ai_data["summary"],
        actions=ai_data["actions"],
    )
