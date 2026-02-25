from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import os

MAX_TRANSCRIPT_LENGTH = int(os.getenv("MAX_TRANSCRIPT_LENGTH", "200000"))
# On récupère la string brute d'abord
raw_langs = os.getenv("ALLOWED_LANGUAGES", "fr,en") #LIGNE MODIFIEE : au lieu de split("") dans le code d'origine. 
# On split la string et on nettoie les espaces
ALLOWED_SET = {x.strip() for x in raw_langs.split(",") if x.strip()}

class MeetingSummaryRequest(BaseModel):
    meeting_id: str = Field()
    transcript: str = Field(min_length=1, max_length=200000) 
    language: Optional[str] = None
    
    @field_validator("meeting_id")
    @classmethod
    def validate_meeting_id(cls, v: str):
        v2 = v.strip()
        if not v2:
            raise ValueError("Meeting ID is required and cannot be empty.")
        return v2
    
    @field_validator("transcript")
    @classmethod
    def validate_transcript(cls, v: str) -> str:
        if len(v) > MAX_TRANSCRIPT_LENGTH:
            raise ValueError(f"Transcript exceeds maximum length of {MAX_TRANSCRIPT_LENGTH} characters.")
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
            raise ValueError(f"Language '{v}' is not supported. Allowed languages are: {sorted(ALLOWED_SET)}.")
        return v2

class ActionItem(BaseModel):
    owner: str = Field(min_length=1)
    description: str = Field(min_length=1)

class MeetingSummaryResponse(BaseModel):
    meeting_id: str
    summary: str
    actions: List[ActionItem]