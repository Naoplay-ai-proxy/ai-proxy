from pydantic import BaseModel, Field,field_validator
from typing import List, Optional
import os
import re

MAX_TRANSCRIPT_LENGTH = int(os.getenv("MAX_TRANSCRIPT_LENGTH", "200000"))
ALLOWED_LANGUAGES = os.getenv("ALLOWED_LANGUAGES", "fr,en").split(",")
ALLOWED_SET={
    lang.strip()
    for lang in os.getenv("ALLOWED_LANGUAGES", "fr,en").split(",")
    if lang.strip()
}

MEETING_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

# Détection XSS / patterns malveillants 
MALICIOUS_TRANSCRIPT_RE = re.compile(
    r"(?is)<\s*script\b|</\s*script\s*>|javascript\s*:|on\w+\s*=",)
    
# Détection de patterns d'injection sémantique / prompt injection
PROMPT_INJECTION_RE = re.compile(
    r"(?is)"
    r"\bignore\s+previous\s+instructions\b"
    r"|"
    r"\bsystem\s+prompt\b"
    r"|"
    r"\bwithout\s+safety\s+filters\b"
    r"|"
    r"\badmin\s+access\b"
)

class MeetingSummaryRequest(BaseModel):
    

    meeting_id: str = Field(min_length=1, max_length=64)
    transcript: str = Field(min_length=1, max_length=MAX_TRANSCRIPT_LENGTH) 
    language: Optional[str] = None
    
    # id non vide et non null
    @field_validator("meeting_id")
    @classmethod
    def validate_meeting_id(cls, v: str):
        v2 = v.strip()
        if not v2:
            raise ValueError("Meeting ID is required and cannot be empty.")
        if not MEETING_ID_PATTERN.match(v2):
            raise ValueError(
                "Meeting ID contains forbidden characters"
            )
        return v2
    
    # transcript non vide et non null et pas trop long
    @field_validator("transcript")
    @classmethod
    def validate_transcript(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("Transcript is required and cannot be empty.")
        # max_length est déjà géré par Field, mais garder ce check ne fait pas de mal
        if len(v2) > MAX_TRANSCRIPT_LENGTH:
            raise ValueError(f"Transcript exceeds maximum length of {MAX_TRANSCRIPT_LENGTH}.")
        
        if MALICIOUS_TRANSCRIPT_RE.search(v2) or  PROMPT_INJECTION_RE.search(v2):
            raise ValueError("Security Alert: Malicious pattern detected in transcript.")

        return v2
    
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
