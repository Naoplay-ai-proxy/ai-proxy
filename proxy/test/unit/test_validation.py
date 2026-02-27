import pytest
from pydantic import ValidationError
from proxy.app.schemas.meeting_summary import MeetingSummaryRequest

# Test 1 : Cas nominal (Tout va bien)
@pytest.mark.unit
def test_valid_request():
    req = MeetingSummaryRequest(
        meeting_id="meet-123", 
        transcript="Ceci est une courte transcription.", 
        language="fr"
    )
    assert req.meeting_id == "meet-123"
    assert req.language == "fr"

# Test 2 : Vérifier qu'une erreur est levée pour une langue invalide
@pytest.mark.unit
def test_invalid_language_raises_error():
    # On dit à pytest : "Je m'attends à ce que ce bloc lève une ValidationError"
    with pytest.raises(ValidationError) as excinfo:
        MeetingSummaryRequest(
            meeting_id="meet-123", 
            transcript="Hello", 
            language="de" # Allemand non supporté
        )
    # On peut même vérifier le message d'erreur si on veut
    assert "Language 'de' is not supported" in str(excinfo.value)

# Test 3 : Vérifier qu'une erreur est levée pour un transcript vide
@pytest.mark.unit
def test_empty_transcript_raises_error():
    with pytest.raises(ValidationError):
        MeetingSummaryRequest(
            meeting_id="meet-123", 
            transcript="", 
            language="en"
        )
