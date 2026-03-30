from fastapi import APIRouter, Depends, Request
from .core.auth import AuthenticatedUser
from .core.security import require_naoplay_user
from .prompt import get_system_prompt
from .schemas.meeting_summary import MeetingSummaryRequest, MeetingSummaryResponse

router = APIRouter()


@router.post("/meeting-summary", response_model=MeetingSummaryResponse)

async def process_meeting_summary(
    request: Request,
    payload: MeetingSummaryRequest,
    user: AuthenticatedUser = Depends(require_naoplay_user),

) -> MeetingSummaryResponse:
    """
    Cet endpoint ne traite la demande qu'après contrôle d'accès,
    afin d'éviter tout coût provider ou traitement métier pour un utilisateur refusé.
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
