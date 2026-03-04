import pytest
from pydantic import ValidationError
from proxy.app.schemas.meeting_summary import MeetingSummaryRequest


@pytest.mark.unit
def test_valid_request():
    req = MeetingSummaryRequest(
        meeting_id="meet-123", 
        transcript="Ceci est une courte transcription.", 
        language="fr"
    )
    assert req.meeting_id == "meet-123"
    assert req.language == "fr"


@pytest.mark.unit
def test_invalid_language_raises_error():
    with pytest.raises(ValidationError) as excinfo:
        MeetingSummaryRequest(
            meeting_id="meet-123", 
            transcript="Hello", 
            language="de" # Allemand non supporté
        )
    assert "Language 'de' is not supported" in str(excinfo.value)


@pytest.mark.unit
def test_empty_transcript_raises_error():
    with pytest.raises(ValidationError):
        MeetingSummaryRequest(
            meeting_id="meet-123", 
            transcript="", 
            language="en"
        )
