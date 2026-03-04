from pydantic import BaseModel, Field,field_validator
from typing import List, Optional
import os

MAX_TRANSCRIPT_LENGTH = int(os.getenv("MAX_TRANSCRIPT_LENGTH", "200000"))
ALLOWED_LANGUAGES = os.getenv("ALLOWED_LANGUAGES", "fr,en").split(",")
ALLOWED_SET={x.strip() for x in ALLOWED_LANGUAGES if x.strip()}

class MeetingSummaryRequest(BaseModel):
    

    meeting_id: str = Field(min_length=1)
    transcript: str = Field(min_length=1, max_length=200000) 
    language: Optional[str] = None
    
    # id non vide et non null
    @field_validator("meeting_id")
    @classmethod
    def validate_meeting_id(cls, v: str):
        v2 = v.strip()
        if not v2:
            raise ValueError("Meeting ID is required and cannot be empty.")
        return v2
    
    # transcript non vide et non null et pas trop long
    @field_validator("transcript")
    @classmethod
    def validate_transcript(cls, v: str) -> str:
        if len(v) > MAX_TRANSCRIPT_LENGTH:
            raise ValueError(f"Transcript exceeds maximum length of {MAX_TRANSCRIPT_LENGTH}.")
        return v
    
    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v2 = v.strip()
        if not v2:
            return None
        if ALLOWED_SET and v2 not in ALLOWED_SET:
            raise ValueError(f"Language '{v}' is not supported. Allowed: {sorted(ALLOWED_SET)}.")
        return v2

class ActionItem(BaseModel):
    owner: str = Field(min_length=1)
    description: str = Field(min_length=1)

class MeetingSummaryResponse(BaseModel):
    meeting_id: str
    summary: str
    actions: List[ActionItem]
