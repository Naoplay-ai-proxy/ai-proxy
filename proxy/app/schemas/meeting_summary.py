from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal

class MeetingSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid") 

    meeting_id: str = Field(min_length=1)
    transcript: str = Field(min_length=1, max_length=50_000) 
    language: Literal["fr", "en"] = "fr"


class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner: str = Field(min_length=1)
    description: str = Field(min_length=1)


class MeetingSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meeting_id: str
    summary: str
    actions: List[ActionItem]
