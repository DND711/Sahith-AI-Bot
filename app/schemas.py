from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SuggestionBase(BaseModel):
    content: str
    priority: str = "normal"


class SuggestionRead(SuggestionBase):
    id: int

    class Config:
        orm_mode = True


class ActionItemBase(BaseModel):
    description: str
    owner: Optional[str] = None
    due_date: Optional[str] = Field(
        default=None, description="Human readable due date captured from transcript"
    )


class ActionItemRead(ActionItemBase):
    id: int

    class Config:
        orm_mode = True


class SummaryRead(BaseModel):
    tldr: str
    discussion: str
    decisions: str
    risks: str

    class Config:
        orm_mode = True


class TranscriptSegmentRead(BaseModel):
    id: int
    position: int
    speaker: Optional[str]
    content: str

    class Config:
        orm_mode = True


class MeetingBase(BaseModel):
    title: str
    scheduled_start: Optional[datetime] = None
    description: Optional[str] = None


class MeetingCreate(MeetingBase):
    pass


class MeetingRead(MeetingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class MeetingDetail(MeetingRead):
    transcript_segments: List[TranscriptSegmentRead]
    summary: Optional[SummaryRead]
    action_items: List[ActionItemRead]
    suggestions: List[SuggestionRead]


class TranscriptIngestionRequest(BaseModel):
    transcript_text: str = Field(..., description="Plain text transcript of the meeting")
    speaker_prefix: Optional[str] = Field(
        default="Speaker", description="Prefix used when detecting speakers"
    )


class SummaryResponse(BaseModel):
    meeting: MeetingRead
    summary: Optional[SummaryRead]
    action_items: List[ActionItemRead]
    suggestions: List[SuggestionRead]


class HealthResponse(BaseModel):
    status: str
    version: str
